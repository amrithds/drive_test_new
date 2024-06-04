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
    this.http.get(this.environment.apiUrl + 'v1/course/get_vehicle_no/').subscribe(
      (data: any) => {
        console.log("Fetched veh no",data);
        this.veh_no = data.vehicle_no.toUpperCase();
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }
}
