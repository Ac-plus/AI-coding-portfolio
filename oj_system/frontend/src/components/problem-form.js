import { splitTags } from "../utils/format.js";

export function problemFormTemplate() {
  return `
    <form id="problem-form" class="problem-form">
      <div class="section-title-row">
        <h3 id="problem-form-title">新增题目</h3>
        <span class="section-tip">使用 JSON 填参数与测试用例</span>
      </div>
      <label>题目 ID<input name="id" placeholder="例如：two-sum-ii" required /></label>
      <label>标题<input name="title" placeholder="例如：两数之和 II" required /></label>
      <label>难度
        <select name="difficulty">
          <option>Easy</option>
          <option selected>Medium</option>
          <option>Hard</option>
        </select>
      </label>
      <label>标签<input name="tags" placeholder="数组, 双指针" required /></label>
      <label>描述<textarea name="description" rows="4" required></textarea></label>
      <label>输入格式<textarea name="input_format" rows="2" required></textarea></label>
      <label>输出格式<textarea name="output_format" rows="2" required></textarea></label>
      <label>提示<textarea name="hint" rows="2"></textarea></label>
      <label>函数名<input name="function_name" placeholder="例如：twoSum" required /></label>
      <label>返回类型<input name="return_type" placeholder="例如：vector<int>" required /></label>
      <label>参数 JSON<textarea name="parameters" rows="4" required>[{"name":"nums","type":"vector<int>"},{"name":"target","type":"int"}]</textarea></label>
      <label>测试用例 JSON<textarea name="test_cases" rows="6" required>[{"input":[[2,7,11,15],9],"expected":[0,1]}]</textarea></label>
      <label>时间限制（ms）<input name="time_limit_ms" type="number" value="1000" min="100" /></label>
      <label>内存限制（MB）<input name="memory_limit_mb" type="number" value="256" min="64" /></label>
      <label>起始代码<textarea name="starter_code" rows="10">#include &lt;vector&gt;
using namespace std;

class Solution {
public:
    vector&lt;int&gt; solve() {
        return {};
    }
};</textarea></label>
      <div class="form-actions">
        <button id="problem-form-submit" type="submit" class="primary-button">保存题目</button>
        <button id="problem-form-cancel" type="button" class="ghost-button">取消编辑</button>
      </div>
      <p id="problem-form-message" class="inline-message"></p>
    </form>
  `;
}

export function collectProblemFormPayload(formElement) {
  const formData = new FormData(formElement);

  return {
    id: formData.get("id").trim(),
    title: formData.get("title").trim(),
    difficulty: formData.get("difficulty").trim(),
    tags: splitTags(formData.get("tags")),
    description: formData.get("description").trim(),
    input_format: formData.get("input_format").trim(),
    output_format: formData.get("output_format").trim(),
    hint: formData.get("hint").trim(),
    function_name: formData.get("function_name").trim(),
    return_type: formData.get("return_type").trim(),
    parameters: JSON.parse(formData.get("parameters")),
    test_cases: JSON.parse(formData.get("test_cases")),
    time_limit_ms: Number(formData.get("time_limit_ms")),
    memory_limit_mb: Number(formData.get("memory_limit_mb")),
    starter_code: formData.get("starter_code"),
    metadata: {
      source: "frontend",
    },
  };
}

export function fillProblemForm(formElement, problem) {
  formElement.elements.id.value = problem.id ?? "";
  formElement.elements.title.value = problem.title ?? "";
  formElement.elements.difficulty.value = problem.difficulty ?? "Medium";
  formElement.elements.tags.value = (problem.tags ?? []).join(", ");
  formElement.elements.description.value = problem.description ?? "";
  formElement.elements.input_format.value = problem.input_format ?? "";
  formElement.elements.output_format.value = problem.output_format ?? "";
  formElement.elements.hint.value = problem.hint ?? "";
  formElement.elements.function_name.value = problem.function_name ?? "";
  formElement.elements.return_type.value = problem.return_type ?? "";
  formElement.elements.parameters.value = JSON.stringify(problem.parameters ?? [], null, 2);
  formElement.elements.test_cases.value = JSON.stringify(problem.test_cases ?? [], null, 2);
  formElement.elements.time_limit_ms.value = problem.time_limit_ms ?? 1000;
  formElement.elements.memory_limit_mb.value = problem.memory_limit_mb ?? 256;
  formElement.elements.starter_code.value = problem.starter_code ?? "";
}

export function setProblemFormMode({
  mode,
  formElement,
  titleElement,
  submitButton,
  cancelButton,
  messageElement,
}) {
  const isEdit = mode === "edit";
  titleElement.textContent = isEdit ? "编辑题目" : "新增题目";
  submitButton.textContent = isEdit ? "更新题目" : "保存题目";
  cancelButton.style.display = isEdit ? "inline-flex" : "none";
  formElement.elements.id.readOnly = isEdit;
  formElement.elements.id.classList.toggle("readonly-input", isEdit);
  if (!isEdit) {
    messageElement.textContent = "";
  }
}
