import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { environment } from '../../environment/environment';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-all-reports',
  templateUrl: './all-reports.component.html',
  styleUrl: './all-reports.component.scss'
})
export class AllReportsComponent {
  public form!: FormGroup;
  public all_reports:boolean=false;
  public courses:any=[];
  public environment = environment;
  public course_id:any;
  public filteredOptions:any = [];
  public selected_option:any;
  sessions: { session: any, reports: any[], numbers: number[],totalMarks: number;timemarks:number;totalobtainedscore:number  }[] = []; 
  public header_num = Array(10).fill(1);
  firstColumn: any[] = [];
  secondColumn: any[] = [];
  public obstacles:any;

  constructor(
    private fb:FormBuilder,
    private http: HttpClient,
  ){}

  ngOnInit() {
    this.fetchCourse();
    
    this.form = this.fb.group({
      course_id: [null,Validators.required],
      from_date: [null,Validators.required],
      to_date: [null],
    });
  }

  calculateTotalMarks(data: any) {
    let total = 0;
    for (let mark of data.numbers) {
      total += parseInt(mark, 10) || 0; // Convert mark to integer, handle NaN scenario
    }
    data.totalMarks = total;
  }

  onKeyDown(event: KeyboardEvent): void {
    const allowedKeys = ['0', '1', 'Backspace'];

    // Allow the key if it's in the allowedKeys array or it's a numerical key
    if (event.key === 'Backspace' || /^[01]$/.test(event.key)) {
      return; // Allow input to proceed
    } else {
      event.preventDefault(); // Prevent the default action (input of the key)
    }
  }

  getreports() {
    this.http.get(this.environment.apiUrl + 'v1/report/finalReport/?course_id=' + this.selected_option.id + '&from_date=' + this.form.value['from_date'] + '&to_date=' + this.form.value['to_date'])
      .subscribe(
        (data: any) => {
          console.log("Final report data:", data);
          if(data.results.length>0){
            this.all_reports=true;
            this.fetchObstacle();

            console.log("Final report data:", data);
          
            // Initialize the sessions object
            const sessions: { session: any, 
              reports: any[], numbers: number[],totalMarks: number;timemarks:number;totalobtainedscore:number  }[] = [];
  
            data.results.forEach((report:any) => {
              const sessionId = report.session.id;
  
              let sessionEntry = sessions.find(s => s.session.id === sessionId);
    
              if (!sessionEntry) {
                sessionEntry = {
                  session: report.session,
                  reports: [],
                  numbers: Array(10).fill(1),
                  totalMarks: 0,
                  timemarks:0,
                  totalobtainedscore:0,
                };
                sessions.push(sessionEntry);
              }
              const existingReportIndex = sessionEntry.reports.findIndex(r => r.obstacle.id === report.obstacle.id);
    
              if (existingReportIndex === -1) {
                sessionEntry.reports.push(report);
              } else {
                sessionEntry.reports[existingReportIndex] = report;
              }
    
            });
            sessions.forEach(session => {
              let totalObstacleDurationInMinutes = 0;
              let totalObstacleDurationInSeconds = 0;
              let totalobtainedscore = 0;
              session.reports.forEach(report => {
                if (report.obstacle_duration !== null) {
                  totalObstacleDurationInSeconds += report.obstacle_duration;
                }
                if (report.obtained_score !== null) {
                  totalobtainedscore += report.obtained_score;
                }
                totalObstacleDurationInMinutes = Math.round(totalObstacleDurationInSeconds/60);
  
              });
              if (totalObstacleDurationInMinutes >= 16 && totalObstacleDurationInMinutes <= 20) {
                session.timemarks = 10;
              } else if (totalObstacleDurationInMinutes > 20 && totalObstacleDurationInMinutes <= 24) {
                session.timemarks = 6;
              } else if (totalObstacleDurationInMinutes > 24 && totalObstacleDurationInMinutes <= 28) {
                session.timemarks = 2;
              } else if (totalObstacleDurationInMinutes > 28){
                session.timemarks = 0;
              }
              session.totalobtainedscore = totalobtainedscore;
              let total = 0;
              session.numbers.forEach(mark => {
                total += mark || 0;
              });
              session.totalMarks = total;           
            });
            this.sessions = sessions;
  
            let totalObstacleDurationInSeconds = 0;
  
            this.sessions.forEach((report: any) => {
              if (report.obstacle_duration !== null) {
                  totalObstacleDurationInSeconds += report.obstacle_duration;
              }
            });
            console.log("Transformed data:", this.sessions);
          }else{
            window.alert("There are no records.")
          }
        },
        (error: any) => {
          console.error('Error fetching data:', error);
        }
      );
  }

  getTotalMarks(): number {
    let totalMarks = 0;
    if(this.sessions.length>0){
      for (const trainee of this.sessions[0].reports) {
        totalMarks += trainee.total_score;
      }
    }
   
    return totalMarks;
  }

  fetchObstacle(){
    this.http.get(this.environment.apiUrl + 'v1/course/obstacle/').subscribe(
      (data: any) => {
        console.log("Fetched obstacles",data.results);
        this.obstacles = data.results.sort((a:any, b:any) => a.order - b.order);
        const halfLength = Math.ceil(this.obstacles.length / 2);
  
        this.firstColumn = this.obstacles.slice(0, halfLength);
        this.secondColumn = this.obstacles.slice(halfLength);
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
    this.course_id = this.form.value['course_id']
    this.filteredOptions = this.courses.filter((course: any) =>
      course.name.toLowerCase().includes(this.course_id?.toLowerCase())
    );
  }
  
  selectOption(option: any): void {
    this.selected_option = option
    this.form.get('course_id')?.setValue(option.name);
    this.course_id = this.form.value['course_id'];
    this.filteredOptions = [];
  }

  print(): void {
    window.print();
  }
}
