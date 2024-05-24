import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { formatDate } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../environment/environment';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../auth.service';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {

  public form!: FormGroup;
  public today= new Date();
  public getDatetime='';
  public response:any;
  public environment = environment;

  constructor(
    private fb:FormBuilder,
    private router:Router,
    private http:HttpClient,
    private authService: AuthService,
  ){
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }
  
  ngOnInit(){
    this.form = this.fb.group({
      username: ['admin',Validators.required],
      password: [null,Validators.required],
    });
  }

  userLogin() {
    if (this.form.valid) {
      firstValueFrom(this.http.post<any>(this.environment.apiUrl + 'v1/course/login/', this.form.value)).then((data: any) => {
        console.log(data);
        const token = data.token;
        if (token) {
          localStorage.setItem('token', token);
        }
        this.router.navigate(['/training'])
      }).catch((error: HttpErrorResponse) => {
        if (error.status === 400) {
          window.alert('Invalid Credentials')
        }
      });
    }
  }

}


