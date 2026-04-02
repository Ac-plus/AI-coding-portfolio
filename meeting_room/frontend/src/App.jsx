import { useEffect, useState } from "react";

import {
  cancelBooking,
  createBooking,
  getBookings,
  getRooms,
  releaseExpiredBookings,
} from "./api/client";
import BookingForm from "./components/BookingForm";
import BookingList from "./components/BookingList";
import Notification from "./components/Notification";
import RoomList from "./components/RoomList";

function toDateTimeLocalValue(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function buildInitialForm() {
  const start = new Date(Date.now() + 60 * 60 * 1000);
  const end = new Date(Date.now() + 2 * 60 * 60 * 1000);
  return {
    user_id: "",
    room_id: "",
    start_time: toDateTimeLocalValue(start),
    end_time: toDateTimeLocalValue(end),
  };
}

export default function App() {
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [selectedRoomId, setSelectedRoomId] = useState("");
  const [currentUserId, setCurrentUserId] = useState("");
  const [form, setForm] = useState(buildInitialForm);
  const [submitting, setSubmitting] = useState(false);
  const [cancellingId, setCancellingId] = useState("");
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [roomData, bookingData] = await Promise.all([getRooms(), getBookings()]);
        setRooms(roomData);
        setBookings(bookingData);
        if (roomData[0]) {
          setSelectedRoomId(roomData[0].id);
          setForm((current) => ({ ...current, room_id: roomData[0].id }));
        }
      } catch (error) {
        setNotification({ tone: "error", message: error.message });
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  async function refreshBookings(userId = currentUserId) {
    const bookingData = await getBookings({ user_id: userId || undefined });
    setBookings(bookingData);
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    if (name === "user_id") {
      setCurrentUserId(value);
    }
    if (name === "room_id") {
      setSelectedRoomId(value);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await createBooking({
        ...form,
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
      });
      await refreshBookings(form.user_id);
      setNotification({ tone: "success", message: "预订已创建。" });
      setCurrentUserId(form.user_id);
    } catch (error) {
      setNotification({ tone: "error", message: error.message });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCancelBooking(booking) {
    setCancellingId(booking.id);
    try {
      await cancelBooking(booking.id, booking.user_id);
      await refreshBookings(currentUserId || booking.user_id);
      setNotification({ tone: "success", message: "预订已取消。" });
    } catch (error) {
      setNotification({ tone: "error", message: error.message });
    } finally {
      setCancellingId("");
    }
  }

  async function handleReleaseExpired() {
    try {
      const payload = await releaseExpiredBookings();
      await refreshBookings(currentUserId);
      setNotification({
        tone: "info",
        message:
          payload.released_count > 0
            ? `已自动释放 ${payload.released_count} 条过期预订。`
            : "当前没有可释放的过期预订。",
      });
    } catch (error) {
      setNotification({ tone: "error", message: error.message });
    }
  }

  async function handleFilterUser(value) {
    setCurrentUserId(value);
    try {
      const bookingData = await getBookings({ user_id: value || undefined });
      setBookings(bookingData);
    } catch (error) {
      setNotification({ tone: "error", message: error.message });
    }
  }

  return (
    <main className="app-shell">
      <div className="layout">
        <section className="hero">
          <p className="eyebrow">Meeting Room Booking</p>
          <h1>会议室预订系统</h1>
          <p className="description">
            当前页面已接入后端 API，支持查看会议室、创建预订、按用户筛选记录、取消预订，以及手动触发过期释放。
          </p>
        </section>

        <Notification
          message={notification?.message}
          tone={notification?.tone}
          onClose={() => setNotification(null)}
        />

        {loading ? (
          <section className="panel loading-panel">正在加载会议室和预订数据...</section>
        ) : (
          <div className="dashboard">
            <div className="dashboard-column">
              <RoomList
                rooms={rooms}
                bookings={bookings}
                selectedRoomId={selectedRoomId}
                onSelectRoom={(roomId) => {
                  setSelectedRoomId(roomId);
                  setForm((current) => ({ ...current, room_id: roomId }));
                }}
              />
              <BookingForm
                form={form}
                rooms={rooms}
                submitting={submitting}
                onChange={handleChange}
                onSubmit={handleSubmit}
                onReleaseExpired={handleReleaseExpired}
              />
            </div>
            <BookingList
              bookings={bookings}
              currentUserId={currentUserId}
              onFilterUser={handleFilterUser}
              onCancelBooking={handleCancelBooking}
              cancellingId={cancellingId}
            />
          </div>
        )}
      </div>
    </main>
  );
}
