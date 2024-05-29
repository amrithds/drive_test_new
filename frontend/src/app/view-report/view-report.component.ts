
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DatePipe, formatDate } from '@angular/common';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';


@Component({
  selector: 'app-view-report',
  templateUrl: './view-report.component.html',
  styleUrls: ['./view-report.component.scss'],
  providers: [DatePipe]
})
export class ViewReportComponent {
  public form!: FormGroup;
  public today = new Date();
  public enabletable: boolean = false;
  public enablereport: boolean = false;
  public showpdf: boolean = false;
  public environment=environment;
  public individual_report:any=[];
  public view_report:any;
  public report_id:any;
  currentPage = 1;
  public report:any=[];

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,

  ) {}

  ngOnInit() {
    this.form = this.fb.group({
      trainee_id: [null,Validators.required],
    });
  }

  getreports() {
    this.http.get(this.environment.apiUrl + 'v1/course/session/?search=' + this.form.value['trainee_id'] + '&status=2').subscribe(
      (data: any) => {
        this.individual_report = data.results;
        if (this.individual_report.length > 0) {
          this.enabletable = true;
          console.log(this.individual_report)
          this.individual_report = this.individual_report.sort((a:any, b:any) => a.id - b.id);
          this.form.reset();
        } else {
          window.alert("Trainee not exist");
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }
  
  pageChanged(pageNumber: number) {
    console.log(pageNumber)
    this.currentPage = pageNumber;
  }

  viewReport(index:any){
    this.enablereport=true;
    this.enabletable=false;
    console.log(index)
    this.view_report = this.individual_report[index]
    this.report_id = this.individual_report[index].id
    console.log(this.view_report)
    this.http.get(this.environment.apiUrl + 'v1/report/finalReport/?session='+this.report_id).subscribe(
      (data: any) => {
        console.log("Fetched session id",data.results);
        this.report = data.results
      //   this.report = [
      //     {
      //         "tasks": [
      //             {
      //                 "name": "Head Light",
      //                 "score": 10,
      //                 "result": 1,
      //                 "remark": "Head light on",
      //             },
      //             {
      //                 "name": "Seat belt",
      //                 "score": 0,
      //                 "result": 2,
      //                 "remark": "",
      //             }
      //         ],
      //         "result": 1,
      //         "total_score": 20,
      //         "obtained_score": 10,
      //         "name": "Starting Point",
      //         "id": 1,
      //         "obstacle_duration":20
      //     },
      //     {
      //         "tasks": [
      //             {
      //                 "name": "Parking",
      //                 "score": 0,
      //                 "result": 2,
      //                 "remark": "Parking Success",
      //             },
      //             {
      //                 "name": "Seat belt",
      //                 "score": 0,
      //                 "result": 0,
      //                 "remark": "",
      //             },
      //             {
      //                 "name": "Hand brake",
      //                 "score": 0,
      //                 "result": 0,
      //                 "remark": "",
      //             }
      //         ],
      //         "status": 2,
      //         "total_score": 35,
      //         "obtained_score": 0,
      //         "name": "Left Parking",
      //         "id": 2,
      //         "obstacle_duration":20
      //     }
      // ]
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  getTotalObtainedMarks(): number {
    let totalObtainedMarks = 0;
    for (const student of this.report) {
      totalObtainedMarks += student.obtained_score;
    }
    return totalObtainedMarks;
  }

  getTotalTimeTaken(): number {
    let totalTimeTaken = 0;
    for (const student of this.report) {
      totalTimeTaken += student.obstacle_duration;
    }
    return totalTimeTaken;
  }

  getTotalMarks(): number {
    let totalMarks = 0;
    for (const trainee of this.report) {
      totalMarks += trainee.total_score;
    }
    return totalMarks;
  }

  generatePDF() {
    const data = document.getElementById('reportContent')!;
    console.log(data)
    html2canvas(data).then(canvas => {
      const imgWidth = 210;
      const imgHeight = canvas.height * imgWidth / canvas.width;

      const contentDataURL = canvas.toDataURL('image/png');
      let pdf = new jsPDF('p', 'mm', 'a4');
      const position = 0;
      pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);

       // Add footer
      pdf.setFontSize(10);
       pdf.text('Smart Skill Driving Technology By | FIRSTSERVE.com | Mob:99000 99100', 50, pdf.internal.pageSize.height - 10); 

      // Open the PDF in a new tab and trigger the print dialog
      const pdfOutput = pdf.output('blob');
      const blobUrl = URL.createObjectURL(pdfOutput);
      
      const printWindow = window.open(blobUrl);
    });
  }

}
