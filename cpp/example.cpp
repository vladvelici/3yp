#include <iostream>
#include <armadillo>

#include <string>

#include <sstream>
#include <fstream>
#include <vector>

using namespace std;
using namespace arma;

/* Needed functions:
 * - compute similarity index from graph
 * - load matrices from file
 * - save matrices from file
 * - load sparse matrix from CSV in the matlab-friendly format
 * - matrix.ValueAt(i,j)
 */


// String space trimming from stackoverflow answer http://stackoverflow.com/a/217605

// trim from start
static inline std::string &ltrim(std::string &s) {
        s.erase(s.begin(), std::find_if(s.begin(), s.end(), std::not1(std::ptr_fun<int, int>(std::isspace))));
        return s;
}

// trim from end
static inline std::string &rtrim(std::string &s) {
        s.erase(std::find_if(s.rbegin(), s.rend(), std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
        return s;
}

// trim from both ends
static inline std::string &trim(std::string &s) {
        return ltrim(rtrim(s));
}

// represent graph as adj matrix.
// can compute the similarity.
// 
// and test different heuristics.

const int LINE_ERR = 5;

// Only comma separated CSV supported.
SpMat<double> read_csv(string path) {
    ifstream inputFile(path);
    string line = "";

    std::vector<int> from;
    std::vector<int> to;

    while (std::getline(inputFile, line)) {
        stringstream lineStream(line);
        string first = "";
        string second = "";

        std::getline(lineStream, first, ',');
        std::getline(lineStream, second, ',');

        trim(first);
        trim(second);

        if (first.length() == 0 || second.length() == 0) {
            throw LINE_ERR;
        }

        int firstNo = atoi(first.c_str());
        int secondNo = atoi(second.c_str());

        from.push_back(firstNo);
        to.push_back(secondNo);
    }

    // I know the number of edges...

    return 0;
}

void changeMatrix(mat& m) {
    m = m+1;
}

int main (int argc, char** argv) {
    mat A = ones<mat>(3,3);

    cout << A << endl;
    changeMatrix(A);

    cout << A << endl;

    return 0;
}







