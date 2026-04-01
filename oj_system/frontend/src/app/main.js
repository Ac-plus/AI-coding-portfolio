import {
  problemFormTemplate,
  collectProblemFormPayload,
  fillProblemForm,
  setProblemFormMode,
} from "../components/problem-form.js";
import {
  appTemplate,
  renderProblemDetail,
  renderProblemList,
  renderSubmission,
  renderTags,
} from "../components/problem-view.js";
import {
  createProblem,
  createSubmission,
  fetchProblem,
  fetchProblems,
  fetchTags,
  updateProblem,
} from "../services/api.js";

const state = {
  problems: [],
  tags: [],
  activeTag: "",
  activeProblemId: "",
  activeProblem: null,
  submission: null,
  loading: false,
  formMode: "create",
};

const root = document.querySelector("#app");
root.innerHTML = appTemplate();
document.querySelector("#problem-form-panel").innerHTML = problemFormTemplate();

const elements = {
  tagList: document.querySelector("#tag-list"),
  problemList: document.querySelector("#problem-list"),
  problemCount: document.querySelector("#problem-count"),
  problemHeader: document.querySelector("#problem-header"),
  problemBody: document.querySelector("#problem-body"),
  codeEditor: document.querySelector("#code-editor"),
  submitButton: document.querySelector("#submit-button"),
  submissionCard: document.querySelector("#submission-card"),
  toggleFormButton: document.querySelector("#toggle-form-button"),
  problemFormPanel: document.querySelector("#problem-form-panel"),
  clearTagButton: document.querySelector("#clear-tag-button"),
  problemForm: document.querySelector("#problem-form"),
  problemFormTitle: document.querySelector("#problem-form-title"),
  problemFormSubmit: document.querySelector("#problem-form-submit"),
  problemFormCancel: document.querySelector("#problem-form-cancel"),
  problemFormMessage: document.querySelector("#problem-form-message"),
};

function syncView() {
  renderTags(elements.tagList, state.tags, state.activeTag);
  renderProblemList(elements.problemList, state.problems, state.activeProblemId);
  renderProblemDetail(elements.problemHeader, elements.problemBody, state.activeProblem);
  renderSubmission(elements.submissionCard, state.submission);
  elements.problemCount.textContent = `${state.problems.length} 题`;
  elements.submitButton.disabled = state.loading || !state.activeProblemId;
  elements.submitButton.textContent = state.loading ? "评测中..." : "提交评测";
  setProblemFormMode({
    mode: state.formMode,
    formElement: elements.problemForm,
    titleElement: elements.problemFormTitle,
    submitButton: elements.problemFormSubmit,
    cancelButton: elements.problemFormCancel,
    messageElement: elements.problemFormMessage,
  });
}

async function loadProblemList() {
  const [problemsResponse, tagsResponse] = await Promise.all([
    fetchProblems(state.activeTag),
    fetchTags(),
  ]);

  state.problems = problemsResponse.items;
  state.tags = tagsResponse.items;

  if (!state.problems.some((item) => item.id === state.activeProblemId)) {
    state.activeProblemId = state.problems[0]?.id || "";
  }

  if (state.activeProblemId) {
    await loadProblemDetail(state.activeProblemId);
  } else {
    state.activeProblem = null;
    state.submission = null;
    elements.codeEditor.value = "";
  }
}

async function loadProblemDetail(problemId) {
  state.activeProblem = await fetchProblem(problemId);
  state.activeProblemId = state.activeProblem.id;
  state.submission = null;
  elements.codeEditor.value = state.activeProblem.starter_code || "";
}

async function handleProblemSelection(problemId) {
  await loadProblemDetail(problemId);
  syncView();
}

async function handleSubmit() {
  if (!state.activeProblemId) {
    return;
  }

  state.loading = true;
  syncView();

  try {
    const submission = await createSubmission(state.activeProblemId, elements.codeEditor.value);
    state.submission = submission;
  } catch (error) {
    state.submission = {
      status: "Compile Error",
      passed: 0,
      total: 0,
      score: 0,
      compile_output: error.message,
      results: [],
    };
  } finally {
    state.loading = false;
    syncView();
  }
}

async function handleCreateProblem(event) {
  event.preventDefault();

  try {
    const payload = collectProblemFormPayload(elements.problemForm);
    if (state.formMode === "edit") {
      await updateProblem(payload.id, payload);
      elements.problemFormMessage.textContent = "题目更新成功，已刷新题库。";
    } else {
      await createProblem(payload);
      elements.problemFormMessage.textContent = "题目创建成功，已刷新题库。";
    }
    await loadProblemList();
    await handleProblemSelection(payload.id);
    resetFormMode();
    syncView();
  } catch (error) {
    elements.problemFormMessage.textContent = `${state.formMode === "edit" ? "更新" : "创建"}失败：${error.message}`;
  }
}

function openFormPanel() {
  elements.problemFormPanel.classList.remove("collapsed");
}

function resetFormMode() {
  state.formMode = "create";
  elements.problemForm.reset();
  elements.problemForm.elements.parameters.value =
    '[{"name":"nums","type":"vector<int>"},{"name":"target","type":"int"}]';
  elements.problemForm.elements.test_cases.value =
    '[{"input":[[2,7,11,15],9],"expected":[0,1]}]';
  elements.problemForm.elements.time_limit_ms.value = 1000;
  elements.problemForm.elements.memory_limit_mb.value = 256;
  elements.problemForm.elements.starter_code.value = `#include <vector>
using namespace std;

class Solution {
public:
    vector<int> solve() {
        return {};
    }
};`;
  elements.problemFormMessage.textContent = "";
}

function enterEditMode() {
  if (!state.activeProblem) {
    return;
  }

  state.formMode = "edit";
  fillProblemForm(elements.problemForm, state.activeProblem);
  elements.problemFormMessage.textContent = "正在编辑当前题目。题目 ID 已锁定。";
  openFormPanel();
  syncView();
}

function bindEvents() {
  elements.tagList.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-tag]");
    if (!button) {
      return;
    }
    state.activeTag = button.dataset.tag;
    await loadProblemList();
    syncView();
  });

  elements.problemList.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-problem-id]");
    if (!button) {
      return;
    }
    await handleProblemSelection(button.dataset.problemId);
  });

  elements.submitButton.addEventListener("click", handleSubmit);

  elements.toggleFormButton.addEventListener("click", () => {
    if (state.formMode !== "create") {
      resetFormMode();
      syncView();
    }
    elements.problemFormPanel.classList.toggle("collapsed");
  });

  elements.problemHeader.addEventListener("click", (event) => {
    if (event.target.closest("#edit-problem-button")) {
      enterEditMode();
    }
  });

  elements.clearTagButton.addEventListener("click", async () => {
    state.activeTag = "";
    await loadProblemList();
    syncView();
  });

  elements.problemForm.addEventListener("submit", handleCreateProblem);
  elements.problemFormCancel.addEventListener("click", () => {
    resetFormMode();
    syncView();
  });
}

async function bootstrap() {
  resetFormMode();
  bindEvents();
  await loadProblemList();
  syncView();
}

bootstrap().catch((error) => {
  elements.problemBody.innerHTML = `<div class="empty-state">页面初始化失败：${error.message}</div>`;
});
