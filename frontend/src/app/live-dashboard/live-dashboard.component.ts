import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-live-dashboard',
  templateUrl: './live-dashboard.component.html',
  styleUrl: './live-dashboard.component.scss'
})
export class LiveDashboardComponent {
  public environment=environment;
  public obstacles:any=[]
  public report:any=[];
  public session:any;
  public old_data:any;
  public intervalId:any;
  public percentage: number = 60;

  constructor(
    private router: Router,
    private http: HttpClient,
    private authService: AuthService
  ){}

  ngOnInit() {
    this.fetchObstacle();
    this.resumeSession();
  }

  fetchObstacle(){
    this.http.get(this.environment.apiUrl + 'v1/course/obstacle/').subscribe(
      (data: any) => {
        console.log("Fetched obstacles",data.results);
        this.obstacles = data.results.sort((a:any, b:any) => a.order - b.order);
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }

  fetchLiveReport() {
    setTimeout(() => {
      this.livereport();
      this.intervalId = setInterval(() => {
        this.livereport();
      }, 2000);
    }, 7000);
  }
  
  livereport() {
    this.http.get(this.environment.apiUrl + 'v1/report/live_report/').subscribe(
      (data: any) => {
        this.report = data
        console.log(this.report)
        for(const obstacle of this.obstacles){
          for(let i = 0; i < this.report.length; i++){
            const report = this.report[i];   
            let resultvalidation = (this.percentage / 100) * report.total_marks;
            if (report.obtained_marks>=resultvalidation){
              report.result = 1
            }else{
              report.result = 2
            }
            if(obstacle.id==report.id){
              obstacle.obstacletaskscore_set = report.tasks
              obstacle.result = report.result
            }
          }
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  resumeSession(){
    this.http.get(this.environment.apiUrl + 'v1/course/current_session/').subscribe(
      (data: any) => {
        console.log("Fetched session in progress",data);
        if(Object.keys(data).length > 0){
          this.fetchLiveReport();
          this.session = data;
        }else{
          console.log("There is no session in progress")
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  getColor(result: number): string {
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
  getDisplayText(content: any): string {
    return content.result == 0 ? content.name : content.remark;
  }

}
