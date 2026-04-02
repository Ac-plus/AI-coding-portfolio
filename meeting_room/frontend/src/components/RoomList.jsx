function formatDateTime(value) {
  return new Date(value).toLocaleString("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function RoomList({
  rooms,
  bookings,
  selectedRoomId,
  onSelectRoom,
  occupancyRange,
  onOccupancyChange,
  occupancyItems,
  onRefreshOccupancy,
}) {
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

      <div className="occupancy-section">
        <div className="panel-heading occupancy-heading">
          <div>
            <p className="panel-eyebrow">Occupancy</p>
            <h2>时间段占用状态</h2>
          </div>
          <button type="button" className="ghost-button" onClick={onRefreshOccupancy}>
            刷新占用状态
          </button>
        </div>

        <div className="occupancy-form">
          <label>
            <span>开始时间</span>
            <input
              type="datetime-local"
              name="start_time"
              value={occupancyRange.start_time}
              onChange={onOccupancyChange}
            />
          </label>
          <label>
            <span>结束时间</span>
            <input
              type="datetime-local"
              name="end_time"
              value={occupancyRange.end_time}
              onChange={onOccupancyChange}
            />
          </label>
        </div>

        <div className="occupancy-list">
          {occupancyItems.map((item) => (
            <div key={item.room_id} className="occupancy-item">
              <div>
                <strong>{item.room_name}</strong>
                <p>
                  {formatDateTime(item.start_time)} - {formatDateTime(item.end_time)}
                </p>
              </div>
              <div className={`status-chip ${item.occupied ? "status-occupied" : "status-active"}`}>
                {item.occupied ? "已占用" : "可预订"}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
