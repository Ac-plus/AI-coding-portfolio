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
using namespace std;

class Solution {
public:
    vector<int> maxPrice(int n, int capacity, vector<int>& weight, vector<int>& price) {
        return vector<int>(n, 0);
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
    int arg_0 = 3; int arg_1 = 10; vector<int> arg_2 = vector<int>{4,6,1}; vector<int> arg_3 = vector<int>{20,50,15};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 1: {
    int arg_0 = 4; int arg_1 = 5; vector<int> arg_2 = vector<int>{2,1,3,2}; vector<int> arg_3 = vector<int>{12,10,20,15};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 2: {
    int arg_0 = 3; int arg_1 = 0; vector<int> arg_2 = vector<int>{1,2,3}; vector<int> arg_3 = vector<int>{5,10,12};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 3: {
    int arg_0 = 1; int arg_1 = 5; vector<int> arg_2 = vector<int>{5}; vector<int> arg_3 = vector<int>{9};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 4: {
    int arg_0 = 3; int arg_1 = 2; vector<int> arg_2 = vector<int>{3,4,5}; vector<int> arg_3 = vector<int>{10,20,30};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 5: {
    int arg_0 = 4; int arg_1 = 20; vector<int> arg_2 = vector<int>{2,3,4,5}; vector<int> arg_3 = vector<int>{3,7,9,10};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 6: {
    int arg_0 = 5; int arg_1 = 9; vector<int> arg_2 = vector<int>{2,3,4,5,9}; vector<int> arg_3 = vector<int>{6,10,12,14,25};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 7: {
    int arg_0 = 5; int arg_1 = 7; vector<int> arg_2 = vector<int>{1,3,4,5,2}; vector<int> arg_3 = vector<int>{1,4,5,7,3};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 8: {
    int arg_0 = 6; int arg_1 = 10; vector<int> arg_2 = vector<int>{6,3,4,2,5,1}; vector<int> arg_3 = vector<int>{30,14,16,9,20,4};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
} case 9: {
    int arg_0 = 7; int arg_1 = 15; vector<int> arg_2 = vector<int>{5,4,6,3,2,7,1}; vector<int> arg_3 = vector<int>{10,40,30,50,35,45,5};
    auto actual = solution.maxPrice(arg_0, arg_1, arg_2, arg_3);
    cout << serialize(actual);
    return 0;
}
                    default:
                        cerr << "Invalid case index";
                        return 1;
                }
            }
