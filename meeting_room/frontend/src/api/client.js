const JSON_HEADERS = { "Content-Type": "application/json" };

export async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: JSON_HEADERS,
    ...options,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const detail =
      payload?.detail?.[0]?.message ||
      payload?.detail?.message ||
      payload?.detail ||
      `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return payload;
}

export function getRooms() {
  return request("/api/rooms");
}

export function getUsers() {
  return request("/api/users");
}

export function getBookings(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  const suffix = search.size ? `?${search.toString()}` : "";
  return request(`/api/bookings${suffix}`);
}

export function createBooking(payload) {
  return request("/api/bookings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function cancelBooking(bookingId, userId) {
  const suffix = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
  return request(`/api/bookings/${bookingId}${suffix}`, {
    method: "DELETE",
  });
}

export function releaseExpiredBookings() {
  return request("/api/maintenance/release-expired", {
    method: "POST",
  });
}

export function getOccupancy(params) {
  const search = new URLSearchParams();
  search.set("start_time", params.start_time);
  search.set("end_time", params.end_time);
  return request(`/api/rooms/occupancy?${search.toString()}`);
}

export function getMetrics() {
  return request("/api/metrics");
}
