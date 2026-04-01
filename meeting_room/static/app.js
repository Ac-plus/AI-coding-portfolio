const messageEl = document.getElementById("message");
const roomSelectEl = document.getElementById("room-select");
const roomsListEl = document.getElementById("rooms-list");
const bookingsBodyEl = document.getElementById("bookings-body");
const bookingFormEl = document.getElementById("booking-form");
const refreshButtonEl = document.getElementById("refresh-button");

let rooms = [];

function showMessage(text, type = "") {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`.trim();
}

function formatTime(value) {
  if (!value) {
    return "-";
  }
  return value.replace("T", " ");
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function renderRooms() {
  roomSelectEl.innerHTML = "";
  roomsListEl.innerHTML = "";

  rooms.forEach((room) => {
    const option = document.createElement("option");
    option.value = room.id;
    option.textContent = `${room.name} (${room.capacity}人)`;
    roomSelectEl.appendChild(option);

    const item = document.createElement("li");
    item.textContent = `${room.name} · 容量 ${room.capacity} 人`;
    roomsListEl.appendChild(item);
  });
}

function renderBookings(bookings) {
  bookingsBodyEl.innerHTML = "";

  if (bookings.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="7">暂无预订记录</td>`;
    bookingsBodyEl.appendChild(row);
    return;
  }

  bookings.forEach((booking) => {
    const room = rooms.find((item) => item.id === booking.room_id);
    const row = document.createElement("tr");
    const buttonHtml =
      booking.status === "active"
        ? `<button data-booking-id="${booking.id}" class="secondary">取消</button>`
        : "-";
    row.innerHTML = `
      <td>${booking.title}</td>
      <td>${booking.user_id}</td>
      <td>${room ? room.name : booking.room_id}</td>
      <td>${formatTime(booking.start_time)}</td>
      <td>${formatTime(booking.end_time)}</td>
      <td>
        <span class="status ${booking.status === "cancelled" ? "cancelled" : ""}">
          ${booking.status}
        </span>
      </td>
      <td>${buttonHtml}</td>
    `;
    bookingsBodyEl.appendChild(row);
  });
}

async function loadRooms() {
  const result = await request("/api/rooms");
  rooms = result.data;
  renderRooms();
}

async function loadBookings() {
  const result = await request("/api/bookings");
  renderBookings(result.data);
}

async function refreshAll() {
  await loadRooms();
  await loadBookings();
}

bookingFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(bookingFormEl);
  const payload = Object.fromEntries(formData.entries());

  try {
    await request("/api/bookings", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showMessage("预订创建成功。", "success");
    bookingFormEl.reset();
    await loadBookings();
  } catch (error) {
    showMessage(error.message, "error");
  }
});

bookingsBodyEl.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const bookingId = target.dataset.bookingId;
  if (!bookingId) {
    return;
  }

  try {
    await request(`/api/bookings/${bookingId}`, {
      method: "DELETE",
    });
    showMessage("预订已取消。", "success");
    await loadBookings();
  } catch (error) {
    showMessage(error.message, "error");
  }
});

refreshButtonEl.addEventListener("click", async () => {
  try {
    await refreshAll();
    showMessage("数据已刷新。", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

async function init() {
  try {
    await refreshAll();
    showMessage("系统已就绪。");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

init();
