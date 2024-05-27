import { Component, OnInit } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormGroup, FormBuilder, FormArray, Validators, FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';
import { Observable, firstValueFrom, map, startWith } from 'rxjs';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-training',
  templateUrl: './training.component.html',
  styleUrl: './training.component.scss'
})
export class TrainingComponent {
  courses:any;
  public today= new Date();
  public getDatetime='';
  public ins_form!: FormGroup;
  public driver_form !: FormGroup;
  public environment=environment;
  public type:any;
  public unique_ref_id:any;
  public course_id:any;
  public searchTerm:string='';
  public instructor_data:any;
  public driver_data:any;
  public startsession:boolean=false;
  public stop_test:boolean=false;
  public trainee_id:any;
  public trainer_id:any;
  filteredOptions: any = [];
  public filteredInsOptions:any=[];
  public users:any;
  public mode:any;
  public filteredDriOptions:any=[];
  public obstacles:any=[]
  public report:any;
  private intervalId: any;
  public session_id:any;
  public items=[
    {
      'ob_name':'STARTING POINT'
    },
    {
      'ob_name':'ZIG-ZAG'
    },
    {
      'ob_name':'SANDWITCH PARKING'
    },
    {
      'ob_name':'NAROW BRIDGE CROSSING'
    },
    {
      'ob_name':'TUNNEL'
    },
    {
      'ob_name':'UP & DOWN HILL'
    },
    {
      'ob_name':'RAILWAY CROSSING'
    },
    {
      'ob_name':'FIGURE OF H'
    },
    {
      'ob_name':'U TURN'
    },
    {
      'ob_name':'SAND PIT'
    },
    {
      'ob_name':'FIGURE OF 8'
    },
    {
      'ob_name':'LEFT REVERSE PARKING'
    },
    {
      'ob_name':'RIGHT REVERSE PARKING'
    },
    {
      'ob_name':'FINISHING POINT'
    },
    {
      'ob_name':'TOTAL MARKS'
    }
  ]
  
  ranks: string[] = ['L Nk', 'Nk', 'L Hav', 'Hav', 'Nb Sub', 'Sub', 'Sub Maj', 'Lt', 'Maj', 'Capt', 'Lt Col'];


  constructor(
    private fb: FormBuilder,
    private router: Router,
    private http: HttpClient,
    private authService: AuthService
  ){
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }

  ngOnInit() {
    this.fetchCourse();
    this.ins_form = this.fb.group({
      mode: [1,Validators.required],
      course: [null,Validators.required],
      id: [null],
      name: [null,Validators.required],
      rank: ['',Validators.required],
      unit: [null,Validators.required],
      unique_ref_id: [null,Validators.required],
      type: [2,Validators.required],
    });

    this.driver_form = this.fb.group({
      id: [null],
      name: [null,Validators.required],
      rank: ['',Validators.required],
      unit: [null,Validators.required],
      unique_ref_id: [null,Validators.required],
      type: [1,Validators.required],
    });
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
    this.course_id = this.ins_form.value['course']
    this.filteredOptions = this.courses.filter((course: any) =>
      course.name.toLowerCase().includes(this.course_id?.toLowerCase())
    );
  }

  selectOption(option: any): void {
    this.ins_form.get('course')?.setValue(option);
    this.course_id = this.ins_form.value['course'];
    this.filteredOptions = [];
    this.fetchUser();
  }

  fetchUser(): void {
    this.http.get(this.environment.apiUrl + 'v1/course/user/?course_id='+this.course_id).subscribe(
      (data: any) => {
        console.log("Fetched Users",data.results);
        this.users = data.results
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  onSearchChangeIns(): void {
    this.unique_ref_id = this.ins_form.value['unique_ref_id']
    console.log(this.unique_ref_id)
    if(this.course_id){
      if(this.unique_ref_id){
        this.filteredInsOptions = this.users.filter((user: any) =>
          user.unique_ref_id.toLowerCase().includes(this.unique_ref_id?.toLowerCase()) &&
          user.type == 2
        );
        console.log(this.filteredInsOptions)
        if(this.filteredInsOptions.length==0){
          this.ins_form.get('unique_ref_id')?.reset()
          window.alert("User not exist")
        }
      }else{
        this.filteredInsOptions = [];
        this.ins_form.get('name')?.reset()
        this.ins_form.get('rank')?.reset()
        this.ins_form.get('unit')?.reset()
      }
    }else{
      window.alert("Please select course id")
      this.ins_form.get('unique_ref_id')?.reset()
    }
  }

  selectOptionIns(option: any): void {
    this.ins_form.get('unique_ref_id')?.setValue(option);
    this.unique_ref_id = this.ins_form.value['unique_ref_id'];
    this.type = this.ins_form.value['type']
    this.filteredInsOptions = [];
    this.fetInsData();
  }

  fetInsData(): void{
    if(this.unique_ref_id){
      this.http.get(this.environment.apiUrl + 'v1/course/user/?course_id='+this.course_id+'&search_id='+this.unique_ref_id+'&type='+this.type).subscribe(
        (data: any) => {
          console.log("Fetched Users",data.results);
          this.instructor_data = data.results
          if(this.instructor_data.length>0){
            this.ins_form.get('name')?.setValue(this.instructor_data[0].name)
            this.ins_form.get('rank')?.setValue(this.instructor_data[0].rank)
            this.ins_form.get('unit')?.setValue(this.instructor_data[0].unit)
            this.trainer_id = this.instructor_data[0].id
          }else{
            this.ins_form.get('name')?.reset()
            this.ins_form.get('rank')?.reset()
            this.ins_form.get('unit')?.reset()
          }
        },
        (error: any) => {
          console.error('Error fetching data:', error);
          window.alert("Please select course id and drive mode")
        }
      );
    }else{
      this.ins_form.get('name')?.reset()
      this.ins_form.get('rank')?.reset()
      this.ins_form.get('unit')?.reset()
    }
  }


  onSearchChangeDri(): void {
    this.unique_ref_id = this.driver_form.value['unique_ref_id']
    console.log(this.unique_ref_id)
    if(this.course_id){
      if(this.unique_ref_id){
        this.filteredDriOptions = this.users.filter((user: any) =>
          user.unique_ref_id.toLowerCase().includes(this.unique_ref_id?.toLowerCase()) &&
          user.type == 1
        );
        console.log(this.filteredDriOptions)
        if(this.filteredDriOptions.length==0){
          this.driver_form.get('unique_ref_id')?.reset()
          window.alert("User not exist")
        }
      }else{
        this.filteredDriOptions = [];
        this.driver_form.get('name')?.reset()
        this.driver_form.get('rank')?.reset()
        this.driver_form.get('unit')?.reset()
      }
    }else{
      window.alert("Please select course id and drive mode")
      this.driver_form.get('unique_ref_id')?.reset()
    }
  }

  selectOptionDri(option: any): void {
    this.driver_form.get('unique_ref_id')?.setValue(option);
    this.unique_ref_id = this.driver_form.value['unique_ref_id'];
    this.type = this.driver_form.value['type']
    this.filteredDriOptions = [];
    this.fetDriData();
  }

  fetDriData(): void{
    this.http.get(this.environment.apiUrl + 'v1/course/user/?course_id='+this.course_id+'&search_id='+this.unique_ref_id+'&type='+this.type).subscribe(
      (data: any) => {
        console.log("Fetched Users",data.results);
        this.driver_data = data.results
        if(this.driver_data.length>0){
          this.driver_form.get('name')?.setValue(this.driver_data[0].name)
          this.driver_form.get('rank')?.setValue(this.driver_data[0].rank)
          this.driver_form.get('unit')?.setValue(this.driver_data[0].unit)
          this.trainee_id = this.driver_data[0].id
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
        window.alert("Please select course id and drive mode")
      }
    );
  }

  fetchObstacle(){
    if(this.ins_form.valid && this.driver_form.valid){
      this.startsession=true;
      this.http.get(this.environment.apiUrl + 'v1/course/obstacle/').subscribe(
        (data: any) => {
          console.log("Fetched obstacles",data.results);
          this.obstacles = data.results
          this.obstacles.push({'name':'Total Marks'})
        },
        (error: any) => {
          console.error('Error fetching data:', error);
        }
      );
    }else{
      console.log(this.ins_form.valid,this.driver_form.valid)
      console.log(this.ins_form.value,this.driver_form.value)
      if(!this.ins_form.valid && !this.driver_form.valid || !this.ins_form.valid){
        window.alert("Enter the instructor ID")
      }else if(!this.driver_form.valid){
        window.alert("Enter the trainee ID")
      }
    }   
  }

  fetchSessionID(){
    this.mode = this.ins_form.value['mode']
    this.startsession=true;
    this.http.get(this.environment.apiUrl + 'v1/course/start_session/?course_id='+this.course_id+'&trainee_id='+this.trainee_id+'&trainer_id='+this.trainer_id+'&mode='+this.mode).subscribe(
      (data: any) => {
        console.log("Fetched session id",data);
        this.stop_test=true;
        this.session_id = data.session_id
        if(this.session_id){
          this.fetchLiveReport();
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  fetchLiveReport(){
    this.intervalId = setInterval(() => {
      this.livereport();
    }, 5000);
  }

  livereport() {
    this.http.get(this.environment.apiUrl + 'v1/report/live_report/').subscribe(
      (data: any) => {
        this.report = data
        console.log(this.report)
      //   this.report = [
      //     {
      //         "tasks": [
      //             {
      //                 "name": "Head Light",
      //                 "score": 10,
      //                 "result": 1,
      //                 "remark": "Head light on",
      //             },
      //             {
      //                 "name": "Seat belt",
      //                 "score": 0,
      //                 "result": 2,
      //                 "remark": "",
      //             }
      //         ],
      //         "status": 1,
      //         "total_marks": 20,
      //         "obtained_marks": 10,
      //         "name": "start",
      //         "id": 1
      //     },
      //     {
      //         "tasks": [
      //             {
      //                 "name": "Parking",
      //                 "score": 0,
      //                 "result": 2,
      //                 "remark": "Parking Success",
      //                 "status": 2,
      //                 "total_marks": 35,
      //                 "obtained_marks": 0,
      //                 "id": 2
      //             },
      //             {
      //                 "name": "Seat belt",
      //                 "score": 0,
      //                 "result": 0,
      //                 "remark": "",
      //                 "status": 2,
      //                 "total_marks": 35,
      //                 "obtained_marks": 0,
      //                 "id": 2
      //             },
      //             {
      //                 "name": "Hand brake",
      //                 "score": 0,
      //                 "result": 0,
      //                 "remark": "",
      //                 "status": 2,
      //                 "total_marks": 35,
      //                 "obtained_marks": 0,
      //                 "id": 2
      //             }
      //         ],
      //         "status": 2,
      //         "total_marks": 35,
      //         "obtained_marks": 0,
      //         "name": "Left Parking",
      //         "id": 2
      //     }
      // ]
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  stopTest(){
    this.http.get(this.environment.apiUrl + 'v1/course/stop_session/?session_id='+this.session_id).subscribe(
      (data: any) => {
        console.log("Fetched session id",data);
        this.stop_test=false;
        window.alert('Test ended successfully');
        clearInterval(this.intervalId);
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  
}
