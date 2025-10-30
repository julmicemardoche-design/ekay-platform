#include <iostream>
using namespace std;

int main() {
    int nombre1, nombre2;
    cout << "Veuillez saisir votre premier nombre";
    cin >> nombre1;
    cout << "Veiller saisir votre deuxieme nombre";
    cin >> nombre2;
    if (nombre1>nombre2)
    cout << "Cette division est impossible, fait en sorte que le deuxieme nombre soit inferieur au premier nombre";
    else{
        if(nombre2==0)
        cout << "il est impossible de diviser un nombre par zero";
    else{
        division = nombre1/nombre2;
        cout <<"la division des nombres donnees sont:" << division;
    }
    }
return 0;
}