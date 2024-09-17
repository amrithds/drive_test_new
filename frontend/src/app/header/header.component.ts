import { Component, Input } from '@angular/core';
import { formatDate } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  @Input() enableBoxShadow: boolean = true;
  public today= new Date();
  public getDatetime='';
  public environment = environment;
  public veh_no:any;
  public left_logo:any=''
  public right_logo:any='';
  public title:any='';
  public subtitle:any='';

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
        if(data){
          this.veh_no = data.results.filter((data:any)=>data.name=="VEHICLE_NUMBER")
          if(this.veh_no){
            this.veh_no = this.veh_no[0].value.toUpperCase();
          }
          this.left_logo = data.results.filter((data:any)=>data.name=="LEFT_LOGO")
          if(this.left_logo){
            this.left_logo = this.left_logo[0].value;
          }else{
            this.left_logo = "army_logo.jpg"
          }
          this.right_logo = data.results.filter((data:any)=>data.name=="RIGHT_LOGO")
          if(this.right_logo){
            this.right_logo = this.right_logo[0].value;
          }else{
            this.right_logo = "kargil_image_1.jpeg"
          }
          this.title = data.results.filter((data:any)=>data.name=="TITLE")
          if(this.title){
            this.title = this.title[0].value;
          }else{
            this.title = "SMART SKILL DRIVING TRACK"
          }
          this.subtitle = data.results.filter((data:any)=>data.name=="SUBTITLE")
          if(this.subtitle){
            this.subtitle = this.subtitle[0].value;
          }
        }       
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }
}
