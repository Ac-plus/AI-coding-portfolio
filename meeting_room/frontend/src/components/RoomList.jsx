export default function RoomList({ rooms, bookings, selectedRoomId, onSelectRoom }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="panel-eyebrow">Rooms</p>
          <h2>会议室列表</h2>
        </div>
      </div>

      <div className="room-grid">
        {rooms.map((room) => {
          const activeCount = bookings.filter(
            (booking) => booking.room_id === room.id && booking.status === "active",
          ).length;

          return (
            <button
              key={room.id}
              type="button"
              className={`room-card ${selectedRoomId === room.id ? "room-card-active" : ""}`}
              onClick={() => onSelectRoom(room.id)}
            >
              <div className="room-card-top">
                <h3>{room.name}</h3>
                <span>{room.location}</span>
              </div>
              <div className="room-card-meta">
                <span>容量 {room.capacity}</span>
                <span>{activeCount} 条有效预订</span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
