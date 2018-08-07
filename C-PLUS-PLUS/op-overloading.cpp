#include <iostream>
using namespace std;






class Box{
private:
	int length,bredth,height;
public:
	int getVol(){
		 return (length*bredth*height);}
	void getlen(int len){
		length = len;}
	void getbre(int br){
		bredth = br; }
	void getheight(int he){
		height =he;}

//overload +operator to add two objects of box type

Box operator+(const Box &b){
	Box box;
	box.length = this->length + b.length;  
	box.bredth = this->bredth + b.bredth;
	box.height = this->height + b.height; //note here "this" is pointer and 
					      //not object so has to be used with -> and not .
	
	return box;
}

};




//Under progress

/*

class Name{
	char *ptr = new name[20];
	char name1[];
	char name2[];

public:
	void getname1(char *ptr){




}



};

*/






int main(){
Box box1;
Box box2;
Box box3;
int volume;

box1.getlen(5);
box1.getbre(4);
box1.getheight(3);


box2.getlen(5);
box2.getbre(4);
box2.getheight(3);

volume = box1.getVol();
cout<<"volume of Box1: " <<volume<<endl;

volume = box2.getVol();
cout<<"volume of Box2: " <<volume<<endl;

box3 = box1 + box2;
volume = box3.getVol();
cout<<"volume of Box3: " <<volume<<endl;



return 0;

}
















