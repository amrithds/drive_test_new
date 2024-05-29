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

  constructor(
    private authService: AuthService
  ){}
  logout() {
    this.authService.logout();
  }

}
