#include <iostream>
using namespace std;

class Emp{
int age,wing,sal;
public:
//parametric constructor takes argument and value is passed to 
//the constructor while instanciating the object
Emp(int a,int w, int s){ 
age=a;
wing=w;
sal=s;
}

void getEmpDetails(){
cout<<"age:"<<age<<endl;
cout<<"wing: "<<wing<<endl;
cout<<"sal: "<<sal<<endl;

}

};

int main(){

//if using parametric constructor, then should pass the proper 
//value while instantiating the object
Emp emp(30,1,10000);  

emp.getEmpDetails();
return 0;
}
