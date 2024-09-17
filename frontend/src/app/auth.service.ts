import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../environment/environment';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  public environment=environment

  constructor(private http: HttpClient, private router: Router) { }

  logout(): void {
    localStorage.removeItem('token');  // Remove the token
    this.router.navigate(['']);  // Redirect to login page
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');  // Check if the token exists
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}
