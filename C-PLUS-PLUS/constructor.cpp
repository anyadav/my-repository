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

//copy constructor
Emp(const Emp &emp){
age=emp.age;
wing=emp.wing;
sal=emp.sal;
}

//NOTE: if you are defining non default constructors then
//it will be mandatory to define the default constructor as well
Emp(){
cout<<"Into default constructor"<<endl;
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
Emp emp(30,1,10000); //here parametric contructor will be called autometically
Emp emp1=emp; //copy constructor will be called here
Emp emp2; //normal default constructor will be called here
emp2=emp;


emp.getEmpDetails();
emp1.getEmpDetails();
emp2.getEmpDetails();

return 0;
}
