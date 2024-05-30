import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, FormArray, Validators, FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';
import { Observable, firstValueFrom, map, startWith } from 'rxjs';

@Component({
  selector: 'app-add-user',
  templateUrl: './add-user.component.html',
  styleUrl: './add-user.component.scss'
})
export class AddUserComponent {
  newUser: any = {};
  public form!: FormGroup;
  public editUserForm !: FormGroup;
  public environment = environment;
  ranks: string[] = ['Rect', 'SEP', 'L Nk', 'Nk', 'L Hav', 'Hav', 'Nb Sub', 'Sub', 'Sub Maj', 'Lt', 'Maj', 'Capt', 'Lt Col'];
  editIndex: number = -1;
  public users:any=[];
  filteredOptions: any = [];
  courses:any;
  course_id:any;
  public searchTerm:any;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.fetchCourse();
    this.form = this.fb.group({
      type: [1],
      course: [null,Validators.required],
      id: [null,Validators.required],
      name: [null,Validators.required],
      rank: [null,Validators.required],
      unit: [null,Validators.required],
      unique_ref_id: [null,Validators.required]
    });

    this.editUserForm  = this.fb.group({
      type: [null],
      course: [null],
      id: [null],
      name: [null],
      rank: [null],
      unit: [null],
      unique_ref_id: [null]
    });
  }

  addUser() {
    if (this.form.valid) {
      const newUser = this.form.value;
      this.users.push(newUser);
      console.log(this.users)
      console.log(this.form.value)
      firstValueFrom(this.http.post(this.environment.apiUrl + 'v1/course/user/', this.form.value)).then((data: any) => {
        console.log(data);
      });
      this.form.get('id')?.reset()
      this.form.get('name')?.reset()
      this.form.get('rank')?.reset()
      this.form.get('unit')?.reset()
      this.form.get('unique_ref_id')?.reset()
    } else {
      window.alert("Please fill the fields")
    }
  }

  editUser(index:any,data:any) {
    console.log(data,index)
    this.editIndex = index;
    this.editUserForm.get('type')?.setValue(data.type)
    this.editUserForm.get('course')?.setValue(data.course)
    this.editUserForm.get('id')?.setValue(data.id)
    this.editUserForm.get('name')?.setValue(data.name)
    this.editUserForm.get('rank')?.setValue(data.rank)
    this.editUserForm.get('unit')?.setValue(data.unit)
    this.editUserForm.get('unique_ref_id')?.setValue(data.unique_ref_id)
  }

  removeUser(index: number) {
    console.log(index,this.users)
    const user_id = this.users[index].id;
    this.http.delete(this.environment.apiUrl+ 'v1/course/user/'+user_id).subscribe(
      () => {
        if (index >= 0 && index < this.users.length) {
          this.users.splice(index, 1);
        }
      },
      (error) => {
        console.error('Error deleting user:', error);
      }
    );
  }

  saveUser() {
    this.editIndex = -1;
    firstValueFrom(this.http.put(this.environment.apiUrl + 'v1/course/user/'+this.editUserForm.value['id']+'/',this.editUserForm.value)).then((data: any) => {
      console.log(data);
      this.course_id = this.form.value['course']
      this.fetchUser(this.course_id);
    });
  }

  cancelEdit() {
    this.editIndex = -1;
  }

  handleChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    console.log(selectedValue);
    this.users=[];
    if(this.searchTerm){
      this.fetchUser(this.searchTerm);
    }
  }

  fetchUser(searchTerm:any): void {
    console.log("searchTerm - ",searchTerm)
    this.searchTerm = searchTerm;
    this.users = [];
    var type = this.form.value['type']
    if(searchTerm !=''){
      this.http.get(this.environment.apiUrl + 'v1/course/user/?course_id='+searchTerm+'&type='+type).subscribe(
        (data: any) => {
          console.log("Fetched Users",data.results);
          this.users = data.results
          this.users = this.users.sort((a:any, b:any) => b.ID - a.ID);
        },
        (error: any) => {
          console.error('Error fetching data:', error);
        }
      );
    }   
  }

  fetchCourse() { 
    this.http.get(this.environment.apiUrl + 'v1/course/course/').subscribe(
      (data: any) => {
        console.log("Fetched course",data.results);
        this.courses = data.results
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }

  onSearchChange(): void {
    this.course_id = this.form.value['course']
    this.filteredOptions = this.courses.filter((course: any) =>
      course.name.toLowerCase().includes(this.course_id?.toLowerCase())
    );
  }

  selectOption(option: any): void {
    this.form.get('course')?.setValue(option);
    this.filteredOptions = [];
    this.fetchUser(option);
  }
}
