import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient,HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../environment/environment';
import { firstValueFrom} from 'rxjs';
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
  ranks: string[] = ['AV', 'Rect', 'SEP', 'L Nk', 'Nk', 'Hav', 'Nb Sub', 'Sub', 'Sub Maj', 'Lt',  'Capt', 'Maj', 'Lt Col', 'Col'];
  editIndex: number = -1;
  public users:any=[];
  filteredOptions: any = [];
  courses:any;
  public searchTerm:any;
  public user_id:any;
  public edituser:boolean=false;
  public type:any;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.fetchCourse();
    this.form = this.fb.group({
      type: [1],
      course: [null],
      serial_no: [null,Validators.required],
      name: [null,Validators.required],
      rank: [null,Validators.required],
      unit: [null,Validators.required],
      unique_ref_id: [null,Validators.required]
    });

    this.editUserForm  = this.fb.group({
      type: [null],
      course: [null],
      serial_no: [null],
      name: [null],
      rank: [null],
      unit: [null],
      unique_ref_id: [null]
    });
  }

  addUser() {
    if(this.form.value['type'] == 1 ){
      this.form.get('course')?.setValidators(Validators.required);
    }else{
      this.form.get('course')?.clearValidators();
    }
    this.form.get('course')?.updateValueAndValidity();
    console.log(this.form.valid,this.form.value)
    if (this.form.valid) {
      const newUser = this.form.value;
      firstValueFrom(this.http.post(this.environment.apiUrl + 'v1/course/user/', this.form.value)).then((data: any) => {
        console.log("User Added")
        this.users.push(newUser);
        if(this.form.value['type'] == 1 ){
          this.fetchUser(this.form.value['course']);
          this.fetchCourse();
        }else{
          this.fetchInsUser();
        }
      }).catch((error: HttpErrorResponse) => {
        if (error.status === 400) {
          window.alert('Army no or serial no already exist')
        }
      });
      this.form.get('serial_no')?.reset()
      this.form.get('name')?.reset()
      this.form.get('rank')?.reset()
      this.form.get('unit')?.reset()
      this.form.get('unique_ref_id')?.reset()
    } else {
      window.alert("Please fill the fields")
    }
  }

  editUser(index:any,data:any) {
    this.user_id = data.id;
    this.edituser = true;
    this.editIndex = index;
    this.editUserForm.get('type')?.setValue(data.type)
    this.editUserForm.get('course')?.setValue(data.course)
    this.editUserForm.get('serial_no')?.setValue(data.serial_no)
    this.editUserForm.get('name')?.setValue(data.name)
    this.editUserForm.get('rank')?.setValue(data.rank)
    this.editUserForm.get('unit')?.setValue(data.unit)
    this.editUserForm.get('unique_ref_id')?.setValue(data.unique_ref_id)
  }

  removeUser(index: number) {
    // console.log(index,this.users)
    const user_id = this.users[index].id;
    this.http.delete(this.environment.apiUrl+ 'v1/course/user/'+user_id+'/').subscribe(
      () => {
        if (index >= 0 && index < this.users.length) {
          this.users.splice(index, 1);
        }
        console.log("User deleted")
      },
      (error) => {
        console.error('Error deleting user:', error);
      }
    );
  }

  saveUser() {
    this.editIndex = -1;
    if(!this.edituser){
      this.user_id = this.editUserForm.value['serial_no']
    }
    this.type = this.editUserForm.value['type']
    firstValueFrom(this.http.put(this.environment.apiUrl + 'v1/course/user/'+this.user_id+'/',this.editUserForm.value)).then((data: any) => {
      console.log("User saved successfully!");
      if(this.type==1){
        this.fetchUser(this.form.value['course']);
      }else{
        this.fetchInsUser();
      }
    });
  }

  cancelEdit() {
    this.editIndex = -1;
  }

  handleChange(event: Event) {
    var selectedValue = (event.target as HTMLSelectElement).value;
    console.log(selectedValue)
    this.users=[];
    if(selectedValue=='2'){
      this.form.get("course")?.reset();
      this.searchTerm = '';
      this.fetchInsUser();
    }else{
      if(this.searchTerm)
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
          console.log("Fetched Dri Users",data.results);
          this.users = data.results
          this.users = this.users.sort((a:any, b:any) => b.ID - a.ID);
        },
        (error: any) => {
          console.error('Error fetching data:', error);
        }
      );
    }   
  }

  fetchInsUser(): void {
    this.users = [];
    this.http.get(this.environment.apiUrl + 'v1/course/user/?type='+this.form.value['type']).subscribe(
      (data: any) => {
        console.log("Fetched Ins Users",data.results);
        this.users = data.results.sort((a:any, b:any) => b.ID - a.ID);
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
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
    if(this.form.value['course']){
      this.filteredOptions = this.courses.filter((course: any) =>
        course.name.toLowerCase().includes(this.form.value['course']?.toLowerCase())
      );
    }else{
      this.filteredOptions = [];
      this.users = [];
    }

  }

  selectOption(option: any): void {
    this.form.get('course')?.setValue(option);
    this.filteredOptions = [];
    this.fetchUser(option);
  }
}
