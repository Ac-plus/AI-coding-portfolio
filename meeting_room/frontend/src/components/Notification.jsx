export default function Notification({ message, tone = "info", onClose }) {
  if (!message) {
    return null;
  }

  return (
    <div className={`notification notification-${tone}`}>
      <div>
        <p className="notification-label">
          {tone === "error" ? "操作失败" : tone === "success" ? "操作成功" : "系统消息"}
        </p>
        <p className="notification-message">{message}</p>
      </div>
      <button type="button" className="ghost-button" onClick={onClose}>
        关闭
      </button>
    </div>
  );
}
