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


def main() -> None:
    problem_service = ProblemService()
    submission_service = SubmissionService()

    problems = problem_service.list_problems()
    tags = problem_service.list_tags()
    result = submission_service.create_submission(
        problem_service.get_problem("two-sum"),
        ACCEPTED_CODE,
    )

    print("problems:", problems)
    print("tags:", tags)
    print("submission:", {key: result[key] for key in ("status", "passed", "total", "score")})


if __name__ == "__main__":
    main()
