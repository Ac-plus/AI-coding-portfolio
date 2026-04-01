const JSON_HEADERS = {
  "Content-Type": "application/json",
};

async function request(path, options = {}) {
  const response = await fetch(path, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null
        ? payload.message || payload.error || "请求失败"
        : "请求失败";
    throw new Error(message);
  }

  return payload;
}

export function fetchProblems(tag = "") {
  const query = tag ? `?tag=${encodeURIComponent(tag)}` : "";
  return request(`/api/problems${query}`);
}

export function fetchProblem(problemId) {
  return request(`/api/problems/${problemId}`);
}

export function fetchTags() {
  return request("/api/tags");
}

export function createSubmission(problemId, sourceCode) {
  return request("/api/submissions", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({
      problem_id: problemId,
      source_code: sourceCode,
    }),
  });
}

export function createProblem(problem) {
  return request("/api/problems", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(problem),
  });
}

export function updateProblem(problemId, problem) {
  return request(`/api/problems/${problemId}`, {
    method: "PUT",
    headers: JSON_HEADERS,
    body: JSON.stringify(problem),
  });
}
