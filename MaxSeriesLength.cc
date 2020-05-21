
#include <iostream>

#include <string>
#include <vector>

using namespace std;

bool GetBit(int num, int place) {
    return num & (1 << place);
    
}
int CountFollwingBits(int num, int size){
    int max_len = 1;
    int len = 1;
    bool current = GetBit(num, 0);
    for(int i = 1; i< size; i++) {
        if(current == GetBit(num,i)) {
            len++;
            //cout << "len = " << len << endl;
            max_len = max(max_len, len);
        } else {
            current = GetBit(num,i);
            len = 1;
        }
    }
    return max_len;
    
}

int main() {
    cout << GetBit(15, 0);
    cout << GetBit(15, 1);
    cout << GetBit(15, 2);
    cout << GetBit(15, 3);
    cout << GetBit(15, 4);
    cout << GetBit(10, 0);
    cout << GetBit(15, 1) << endl;
    
    cout << CountFollwingBits(15, 4) << endl;
    cout << CountFollwingBits(16, 4) << endl;
    cout << CountFollwingBits(0x200, 10) << endl;
    
    const int MAX = 30;
    
    vector<int> freq(MAX + 1);
    double sum = 0;
    for(int i = 0 ;i < 1 << MAX; i++) {
        int res = CountFollwingBits(i, MAX);
        if( res == 1) {
            cout << i << endl;
        }
        sum += res;
        freq[res]++;
    }
    cout << "average" <<  sum / (1 << MAX) << endl;
    for (int i = 0; i < MAX + 1; i++) {
        cout << i << " " << freq[i] << endl;
    }
}
