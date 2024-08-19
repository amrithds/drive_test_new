
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DatePipe } from '@angular/common';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';


@Component({
  selector: 'app-view-report',
  templateUrl: './view-report.component.html',
  styleUrls: ['./view-report.component.scss'],
  providers: [DatePipe]
})
export class ViewReportComponent {
  public form!: FormGroup;
  public enabletable: boolean = false;
  public enablereport: boolean = false;
  public showpdf: boolean = false;
  public environment=environment;
  public individual_report:any=[];
  public view_report:any;
  public report_id:any;
  public currentPage = 1;
  public report:any=[];
  public filteredOptions: any = [];
  public filteredInsOptions:any=[];
  public users:any=[];
  public percentage: number = 60;


  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
  ) {}

  ngOnInit() {
    this.fetchUser();
    this.form = this.fb.group({
      trainee_id: [null,Validators.required],
    });
  }

  fetchUser(): void {
    this.http.get(this.environment.apiUrl + 'v1/course/user/').subscribe(
      (data: any) => {
        console.log("Fetched Users",data.results);
        this.users = data.results
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  onSearchChange(): void {
    let trainee_id = this.form.value['trainee_id']
    console.log(trainee_id)
    if(trainee_id){
      this.filteredOptions = this.users.filter((user: any) =>
        user.unique_ref_id.includes(trainee_id) &&
        user.type == 1
      );
      console.log(this.filteredOptions)
      if(this.filteredOptions.length==0){
        this.form.get('trainee_id')?.reset()
        window.alert("User not exist")
      }
    }else{
      this.filteredOptions = [];
    }
  }

  selectOption(option: any): void {
    this.form.get('trainee_id')?.setValue(option);
    this.filteredOptions = [];
  }

  getreports() {
    this.http.get(this.environment.apiUrl + 'v1/course/session/?search=' + this.form.value['trainee_id'] + '&status=2').subscribe(
      (data: any) => {
        this.individual_report = data.results;
        if (this.individual_report.length > 0) {
          this.enabletable = true;
          console.log(this.individual_report)
          // this.individual_report = this.individual_report.sort((a:any, b:any) => a.id - b.id);
          this.form.reset();
        } else {
          window.alert("Trainee not exist");
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }
  
  pageChanged(pageNumber: number) {
    console.log(pageNumber)
    this.currentPage = pageNumber;
  }

  viewReport(item:any){
    console.log(item)
    this.enablereport=true;
    this.enabletable=false;
    this.view_report = item
    this.report_id = item.id
    this.http.get(this.environment.apiUrl + 'v1/report/finalReport/?session='+this.report_id).subscribe(
      (data: any) => {
        console.log("Fetched session id",data.results);
        this.report = data.results;
        const uniqueReports = this.removeDuplicates(data.results, 'id');
        this.report = uniqueReports;

        const averageSpeed = 25; // km/h
        const speedModifiers = [1, 2, 3, -1, -2];
        for(let i = 0; i < this.report.length; i++){
          const report = this.report[i];
          if(report.obstacle_duration!=0 && report.obstacle_duration!=null){
            const durationInHours = report.obstacle_duration / 3600; // Convert seconds to hours
            const distance = averageSpeed * durationInHours; // Distance in km
            const speed = distance / durationInHours; // Speed in km/h
            const roundedSpeed = Math.round(speed * 100) / 100; // Round to 2 decimal places
    
            if (i < speedModifiers.length) {
              report.speed = roundedSpeed + speedModifiers[i];
            } else {
              report.speed = roundedSpeed; // Default to rounded speed if not enough modifiers
            }
          }else{
            report.speed = 0
          }

          if(report.obstacle_duration!=0 && report.obstacle_duration!=null){
            report.obstacle_duration = Math.round(report.obstacle_duration / 60)
          }

          let resultvalidation = (this.percentage / 100) * report.total_score;
          if (report.obtained_score>=resultvalidation){
            report.result = 1
          }else{
            report.result = 2
          }
          
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  removeDuplicates(array: any[], key: string) {
    const seen = new Map();
    let filteredArray:any = [];
    array.forEach(item => {
      const val = item.obstacle[key];
      if (!seen.has(val)) {
        seen.set(val, true);
        filteredArray.push(item);
      }
    });
    return filteredArray;
  }


  getTaskColor(result: number): string {
    if (result === 0) return 'grey';
    if (result === 1) return 'green';
    if (result === 2) return 'red';
    return 'grey';
  }

  getObsColor(result: number): string {
    if (result === 0) return 'black';
    if (result === 1) return 'green';
    if (result === 2) return 'black';
    return 'black';
  }

  getTotalObtainedMarks(): number {
    let totalObtainedMarks = 0;
    for (const student of this.report) {
      totalObtainedMarks += student.obtained_score;
    }
    return totalObtainedMarks;
  }

  getTotalTimeTaken(): number {
    let totalTimeTaken = 0;
    for (const student of this.report) {
      totalTimeTaken += student.obstacle_duration;
    }
    return totalTimeTaken;
  }

  getTotalTimeMarks(): number {
    let totalObstacleDurationInMinutes = 0;
    // let totalObstacleDurationInSeconds = 0;
    let time_marks = 0;
    for (const student of this.report) {
      // totalObstacleDurationInSeconds += student.obstacle_duration;
      totalObstacleDurationInMinutes += student.obstacle_duration;
    }
    // totalObstacleDurationInMinutes = Math.round(totalObstacleDurationInSeconds/60);
    if (totalObstacleDurationInMinutes >= 16 && totalObstacleDurationInMinutes <= 20) {
      time_marks = 10;
    } else if (totalObstacleDurationInMinutes > 20 && totalObstacleDurationInMinutes <= 24) {
      time_marks = 6;
    } else if (totalObstacleDurationInMinutes > 24 && totalObstacleDurationInMinutes <= 28) {
      time_marks = 2;
    } else if (totalObstacleDurationInMinutes > 28){
      time_marks = 0;
    }
    return time_marks;
  }

  getTotalMarks(): number {
    let totalMarks = 0;
    for (const trainee of this.report) {
      totalMarks += trainee.total_score;
    }
    return totalMarks;
  }

  getSpeed(): number{
    let totalTimeTaken = 0;
    for (const student of this.report) {
      totalTimeTaken += student.speed;
    }
    return totalTimeTaken;
  }

  print(): void{
    window.print()
  }

}
