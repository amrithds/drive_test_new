import { Component } from '@angular/core';
import { formatDate } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  public today= new Date();
  public getDatetime='';
  public environment = environment;
  public veh_no:any;

  constructor(
    private http: HttpClient
  ){
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }

  ngOnInit(){
    this.get_veh_no();
  }

  get_veh_no() { 
    this.http.get(this.environment.apiUrl + 'v1/app_config/config/').subscribe(
      (data: any) => {
        // console.log("Fetched veh no",data);
        if(data){
          this.veh_no = data.results.filter((data:any)=>data.name=="VEHICLE_NUMBER")
          if(this.veh_no){
            this.veh_no = this.veh_no[0].value.toUpperCase();
          }
        }       
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }
}
