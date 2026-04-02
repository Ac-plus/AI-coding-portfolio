import { useEffect, useState } from "react";

import {
  cancelBooking,
  createBooking,
  getBookings,
  getMetrics,
  getOccupancy,
  getRooms,
  getUsers,
  releaseExpiredBookings,
} from "./api/client";
import BookingForm from "./components/BookingForm";
import BookingList from "./components/BookingList";
import MetricsPanel from "./components/MetricsPanel";
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
  const [users, setUsers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [occupancyItems, setOccupancyItems] = useState([]);
  const [selectedRoomId, setSelectedRoomId] = useState("");
  const [currentUserId, setCurrentUserId] = useState("");
  const [form, setForm] = useState(buildInitialForm);
  const [occupancyRange, setOccupancyRange] = useState({
    start_time: buildInitialForm().start_time,
    end_time: buildInitialForm().end_time,
  });
  const [submitting, setSubmitting] = useState(false);
  const [cancellingId, setCancellingId] = useState("");
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    async function bootstrap() {
      try {
        const [roomData, bookingData, userData, metricsData] = await Promise.all([
          getRooms(),
          getBookings(),
          getUsers(),
          getMetrics(),
        ]);
        setRooms(roomData);
        setBookings(bookingData);
        setUsers(userData);
        setMetrics(metricsData.counters || {});
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
    const metricsData = await getMetrics();
    setMetrics(metricsData.counters || {});
  }

  async function refreshOccupancy(range = occupancyRange) {
    const payload = await getOccupancy({
      start_time: new Date(range.start_time).toISOString(),
      end_time: new Date(range.end_time).toISOString(),
    });
    setOccupancyItems(payload);
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
      await refreshOccupancy();
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

  function handleOccupancyChange(event) {
    const { name, value } = event.target;
    setOccupancyRange((current) => ({ ...current, [name]: value }));
  }

  useEffect(() => {
    if (!loading) {
      refreshOccupancy().catch((error) => {
        setNotification({ tone: "error", message: error.message });
      });
    }
  }, [loading]);

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
                occupancyRange={occupancyRange}
                occupancyItems={occupancyItems}
                onSelectRoom={(roomId) => {
                  setSelectedRoomId(roomId);
                  setForm((current) => ({ ...current, room_id: roomId }));
                }}
                onOccupancyChange={handleOccupancyChange}
                onRefreshOccupancy={() => refreshOccupancy().catch((error) => {
                  setNotification({ tone: "error", message: error.message });
                })}
              />
              <BookingForm
                form={form}
                rooms={rooms}
                users={users}
                submitting={submitting}
                onChange={handleChange}
                onSubmit={handleSubmit}
                onReleaseExpired={handleReleaseExpired}
              />
              <MetricsPanel metrics={metrics} />
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
