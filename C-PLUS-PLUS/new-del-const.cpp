#include<iostream>
using namespace std;

class NewDel{
public:
int *arr, *ptr;
int count;

//contructure, lets allocate memory in constructur. 
NewDel(){
arr = new int[10]; //array of 10 integers...while delete have to call like delete[]arr;
ptr = new int(20); //create memory for integer and initialize the int to value 20, 
			//while memory free simply call delete ptr;
cout<< *ptr<<endl;
cout<<arr[0]<<endl;	
}			

void setarr(){

for(count =0; count<10;count++){
arr[count]=count;
}
}

void showarr(){
for(int index=0;index<10;index++){cout<< arr[index]<<" " ;
}
cout<<endl;
}


~NewDel()
{
delete []arr;
delete ptr;
cout<<"Memory pointed by ptr and arr deleted by destructur"<<endl;
}

};



int main(){

NewDel  ob; //as soon you create an object of the class, contructure gets called.
NewDel *obptr;//If you create an object pointer, that does not call the contructur


obptr=&ob;
ob.setarr();  //call member using object
ob.showarr();

obptr->setarr(); // call member using pointer object
obptr->showarr();

return 0;

}
















/*

int main(){
int *ptr = new int(10);
cout<<*ptr<<endl;
//int *ptr = new int[10];

for(int count = 0;count <10;count++){
ptr[count]=count;
cout<<count<<endl;
}

cout<<ptr<<endl;
delete ptr;
return 0;

}



*/
