import { Component } from '@angular/core';
import { formatDate } from '@angular/common';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-menubar',
  templateUrl: './menubar.component.html',
  styleUrl: './menubar.component.scss'
})
export class MenubarComponent {

  public today= new Date();
  public getDatetime='';

  constructor(
    private authService: AuthService
  ){
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }
  logout() {
    this.authService.logout();
  }

}
