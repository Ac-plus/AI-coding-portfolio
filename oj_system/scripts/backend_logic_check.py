from backend.src.services.problem_service import ProblemService
from backend.src.services.submission_service import SubmissionService


ACCEPTED_CODE = """#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;
        for (int i = 0; i < (int)nums.size(); ++i) {
            int need = target - nums[i];
            if (seen.count(need)) return {seen[need], i};
            seen[nums[i]] = i;
        }
        return {};
    }
};
"""

WRONG_ANSWER_CODE = """#include <vector>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        return {0, 0};
    }
};
"""

COMPILE_ERROR_CODE = """class Solution {
public:
    int twoSum( {
        return 0;
    }
};
"""


def main() -> None:
    problem_service = ProblemService()
    submission_service = SubmissionService()
    problem = problem_service.get_problem("two-sum")
    original_hint = problem.hint

    accepted = submission_service.create_submission(problem, ACCEPTED_CODE)
    wrong_answer = submission_service.create_submission(problem, WRONG_ANSWER_CODE)
    compile_error = submission_service.create_submission(problem, COMPILE_ERROR_CODE)
    updated_problem = problem_service.update_problem(
        "two-sum",
        {
            **problem.to_dict(),
            "hint": "可以先用哈希表记录已经遍历过的数字和下标。",
        },
    )

    assert accepted["status"] == "Accepted", accepted
    assert accepted["passed"] == 3, accepted
    assert wrong_answer["status"] == "Wrong Answer", wrong_answer
    assert wrong_answer["passed"] == 0, wrong_answer
    assert compile_error["status"] == "Compile Error", compile_error
    assert updated_problem["hint"] == "可以先用哈希表记录已经遍历过的数字和下标。", updated_problem
    problem_service.update_problem(
        "two-sum",
        {
            **problem.to_dict(),
            "hint": original_hint,
        },
    )

    print("backend logic check passed")


if __name__ == "__main__":
    main()
