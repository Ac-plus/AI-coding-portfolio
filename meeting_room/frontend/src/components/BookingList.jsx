function formatDateTime(value) {
  return new Date(value).toLocaleString("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_LABELS = {
  active: "有效",
  cancelled: "已取消",
  expired: "已过期",
};

export default function BookingList({
  bookings,
  currentUserId,
  onFilterUser,
  onCancelBooking,
  cancellingId,
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="panel-eyebrow">Bookings</p>
          <h2>我的预订与全部记录</h2>
        </div>
        <input
          className="filter-input"
          value={currentUserId}
          onChange={(event) => onFilterUser(event.target.value)}
          placeholder="输入用户 ID 筛选"
        />
      </div>

      <div className="booking-table">
        <div className="booking-table-head">
          <span>用户</span>
          <span>会议室</span>
          <span>开始</span>
          <span>结束</span>
          <span>状态</span>
          <span>操作</span>
        </div>
        {bookings.length === 0 ? (
          <div className="booking-empty">当前没有匹配的预订记录。</div>
        ) : (
          bookings.map((booking) => (
            <div key={booking.id} className="booking-row">
              <span>{booking.user_id}</span>
              <span>{booking.room_id}</span>
              <span>{formatDateTime(booking.start_time)}</span>
              <span>{formatDateTime(booking.end_time)}</span>
              <span>
                <span className={`status-chip status-${booking.status}`}>
                  {STATUS_LABELS[booking.status] || booking.status}
                </span>
              </span>
              <span>
                {booking.status === "active" ? (
                  <button
                    type="button"
                    className="ghost-button"
                    onClick={() => onCancelBooking(booking)}
                    disabled={cancellingId === booking.id}
                  >
                    {cancellingId === booking.id ? "取消中..." : "取消"}
                  </button>
                ) : (
                  "-"
                )}
              </span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
