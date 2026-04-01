#include <bits/stdc++.h>
            using namespace std;

            string serialize(const string& value) { return value; }
string serialize(const char* value) { return string(value); }
string serialize(bool value) { return value ? "true" : "false"; }

template <typename T>
typename enable_if<is_arithmetic<T>::value && !is_same<T, bool>::value, string>::type
serialize(T value) {
    ostringstream out;
    out << value;
    return out.str();
}

template <typename T>
string serialize(const vector<T>& items) {
    string result = "[";
    for (size_t i = 0; i < items.size(); ++i) {
        if (i > 0) result += ",";
        result += serialize(items[i]);
    }
    result += "]";
    return result;
}

            #include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        return {1};
    }
};

            int main(int argc, char** argv) {
                if (argc < 2) {
                    cerr << "Missing case index";
                    return 1;
                }

                int case_index = stoi(argv[1]);
                Solution solution;

                switch (case_index) {
                    case 0: {
    vector<int> arg_0 = vector<int>{2,7,11,15}; int arg_1 = 9;
    auto actual = solution.twoSum(arg_0, arg_1);
    cout << serialize(actual);
    return 0;
} case 1: {
    vector<int> arg_0 = vector<int>{3,2,4}; int arg_1 = 6;
    auto actual = solution.twoSum(arg_0, arg_1);
    cout << serialize(actual);
    return 0;
} case 2: {
    vector<int> arg_0 = vector<int>{3,3}; int arg_1 = 6;
    auto actual = solution.twoSum(arg_0, arg_1);
    cout << serialize(actual);
    return 0;
}
                    default:
                        cerr << "Invalid case index";
                        return 1;
                }
            }
