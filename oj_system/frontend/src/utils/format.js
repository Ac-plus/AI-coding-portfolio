export function statusTone(status) {
  switch (status) {
    case "Accepted":
      return "success";
    case "Wrong Answer":
      return "danger";
    case "Compile Error":
      return "danger";
    case "Runtime Error":
      return "warning";
    case "Time Limit Exceeded":
      return "warning";
    default:
      return "neutral";
  }
}

export function prettyJson(value) {
  return JSON.stringify(value, null, 2);
}

export function splitTags(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
