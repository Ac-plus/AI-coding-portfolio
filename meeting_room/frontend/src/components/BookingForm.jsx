export default function BookingForm({
  form,
  rooms,
  submitting,
  onChange,
  onSubmit,
  onReleaseExpired,
}) {
  return (
    <section className="panel panel-accent">
      <div className="panel-heading">
        <div>
          <p className="panel-eyebrow">Reserve</p>
          <h2>创建预订</h2>
        </div>
        <button type="button" className="ghost-button" onClick={onReleaseExpired}>
          手动释放过期预订
        </button>
      </div>

      <form className="booking-form" onSubmit={onSubmit}>
        <label>
          <span>用户 ID</span>
          <input
            name="user_id"
            value={form.user_id}
            onChange={onChange}
            placeholder="例如 user-1"
            required
          />
        </label>

        <label>
          <span>会议室</span>
          <select name="room_id" value={form.room_id} onChange={onChange} required>
            <option value="">请选择会议室</option>
            {rooms.map((room) => (
              <option key={room.id} value={room.id}>
                {room.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>开始时间</span>
          <input
            type="datetime-local"
            name="start_time"
            value={form.start_time}
            onChange={onChange}
            required
          />
        </label>

        <label>
          <span>结束时间</span>
          <input
            type="datetime-local"
            name="end_time"
            value={form.end_time}
            onChange={onChange}
            required
          />
        </label>

        <button type="submit" className="primary-button" disabled={submitting}>
          {submitting ? "提交中..." : "提交预订"}
        </button>
      </form>
    </section>
  );
}
