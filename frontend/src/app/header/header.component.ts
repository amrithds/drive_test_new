import { Component } from '@angular/core';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  public today= new Date();
  public getDatetime='';
  constructor(
  ){
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }

}
