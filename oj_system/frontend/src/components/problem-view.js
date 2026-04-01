import { statusTone } from "../utils/format.js";
import { markdownToHtml } from "../utils/markdown.js";

export function appTemplate() {
  return `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand-card">
          <div>
            <p class="eyebrow">Lightweight OJ</p>
            <h1>题库与提交</h1>
          </div>
          <button id="toggle-form-button" class="ghost-button">新增题目</button>
        </div>
        <div id="problem-form-panel" class="problem-form-panel collapsed"></div>
        <section class="panel">
          <div class="section-title-row">
            <h2>分类</h2>
            <button id="clear-tag-button" class="link-button">查看全部</button>
          </div>
          <div id="tag-list" class="tag-list"></div>
        </section>
        <section class="panel grow">
          <div class="section-title-row">
            <h2>题目列表</h2>
            <span id="problem-count" class="section-tip"></span>
          </div>
          <div id="problem-list" class="problem-list"></div>
        </section>
      </aside>

      <main class="workspace">
        <section class="problem-pane panel">
          <div id="problem-header"></div>
          <div id="problem-body" class="problem-body"></div>
        </section>

        <section class="editor-pane panel">
          <div class="editor-toolbar">
            <div>
              <p class="eyebrow">C++17</p>
              <h2>代码作答</h2>
            </div>
            <button id="submit-button" class="primary-button">提交评测</button>
          </div>
          <textarea id="code-editor" spellcheck="false"></textarea>
          <div id="submission-card" class="submission-card empty">
            <p>提交后，这里会显示编译结果、通过率和逐用例详情。</p>
          </div>
        </section>
      </main>
    </div>
  `;
}

export function renderTags(container, tags, activeTag) {
  container.innerHTML = tags
    .map(
      (tag) => `
        <button class="tag-chip ${tag === activeTag ? "active" : ""}" data-tag="${tag}">
          ${tag}
        </button>
      `,
    )
    .join("");
}

export function renderProblemList(container, problems, activeProblemId) {
  if (!problems.length) {
    container.innerHTML = `<div class="empty-state">当前分类下还没有题目。</div>`;
    return;
  }

  container.innerHTML = problems
    .map(
      (problem) => `
        <button class="problem-item ${problem.id === activeProblemId ? "active" : ""}" data-problem-id="${problem.id}">
          <div class="problem-item-top">
            <span class="problem-title">${problem.title}</span>
            <span class="difficulty ${problem.difficulty.toLowerCase()}">${problem.difficulty}</span>
          </div>
          <div class="problem-tags">
            ${problem.tags.map((tag) => `<span>${tag}</span>`).join("")}
          </div>
        </button>
      `,
    )
    .join("");
}

export function renderProblemDetail(headerContainer, bodyContainer, problem) {
  if (!problem) {
    headerContainer.innerHTML = `<h2>请选择题目</h2>`;
    bodyContainer.innerHTML = `<div class="empty-state">左侧选择一道题目后，可以在这里查看描述与输入输出要求。</div>`;
    return;
  }

  headerContainer.innerHTML = `
    <div class="problem-meta">
      <div>
        <p class="eyebrow">题目详情</p>
        <h2>${problem.title}</h2>
      </div>
      <div class="meta-badges">
        <button id="edit-problem-button" class="ghost-button" type="button">编辑题目</button>
        <span class="difficulty ${problem.difficulty.toLowerCase()}">${problem.difficulty}</span>
        ${problem.tags.map((tag) => `<span class="outline-badge">${tag}</span>`).join("")}
      </div>
    </div>
  `;

  bodyContainer.innerHTML = `
    <section class="markdown-body">
      <h3>题目描述</h3>
      ${markdownToHtml(problem.description)}
    </section>
    <section class="markdown-body">
      <h3>输入格式</h3>
      ${markdownToHtml(problem.input_format)}
    </section>
    <section class="markdown-body">
      <h3>输出格式</h3>
      ${markdownToHtml(problem.output_format)}
    </section>
    <section class="markdown-body">
      <h3>提示</h3>
      ${markdownToHtml(problem.hint || "暂无提示")}
    </section>
    <section>
      <h3>函数签名</h3>
      <pre><code>${problem.return_type} ${problem.function_name}(${problem.parameters
        .map((item) => `${item.type} ${item.name}`)
        .join(", ")})</code></pre>
    </section>
  `;
}

export function renderSubmission(container, submission) {
  if (!submission) {
    container.className = "submission-card empty";
    container.innerHTML = `<p>提交后，这里会显示编译结果、通过率和逐用例详情。</p>`;
    return;
  }

  const tone = statusTone(submission.status);
  const caseRows = submission.results.length
    ? submission.results
        .map(
          (item) => `
            <tr>
              <td>#${item.case_index + 1}</td>
              <td>${item.status}</td>
              <td><code>${item.expected ?? "-"}</code></td>
              <td><code>${item.actual ?? "-"}</code></td>
            </tr>
          `,
        )
        .join("")
    : `<tr><td colspan="4">当前提交没有可展示的用例结果。</td></tr>`;

  container.className = `submission-card ${tone}`;
  container.innerHTML = `
    <div class="submission-summary">
      <div>
        <p class="eyebrow">评测结果</p>
        <h3>${submission.status}</h3>
      </div>
      <div class="score-block">
        <span>${submission.passed}/${submission.total}</span>
        <strong>${submission.score}</strong>
      </div>
    </div>
    ${
      submission.compile_output
        ? `<section><h4>编译输出</h4><pre><code>${submission.compile_output}</code></pre></section>`
        : ""
    }
    <section>
      <h4>用例详情</h4>
      <table class="result-table">
        <thead>
          <tr><th>用例</th><th>状态</th><th>期望</th><th>实际</th></tr>
        </thead>
        <tbody>${caseRows}</tbody>
      </table>
    </section>
  `;
}
