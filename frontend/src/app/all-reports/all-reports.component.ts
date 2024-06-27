import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { environment } from '../../environment/environment';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-all-reports',
  templateUrl: './all-reports.component.html',
  styleUrl: './all-reports.component.scss'
})
export class AllReportsComponent {
  public form!: FormGroup;
  public all_reports:boolean=false;
  public courses:any=[];
  public environment = environment;
  public course_id:any;
  public filteredOptions:any = [];
  public selected_option:any;

  public center_content:any=[
    {
      "id":"A",
      "name":"STARTING POINT"
    },
    {
      "id":"B",
      "name":"ZIG ZAG TURN"
      },
    {
      "id":"C",
      "name":"SANDWICH PARKING"
    },
    {
      "id":"D",
      "name":"NARROW BRIDGE CROSSING"
    },
    {
      "id":"E",
      "name":"TUNNEL"
    },
    {
      "id":"F",
      "name":"UP & DOWN HILL"
    },
    {
      "id":"G",
      "name":"RAILWAY CROSSING"
    },
    {
      "id":"H",
      "name":"FIGURE OF H"
    },
    {
      "id":"I",
        "name":"U TURN"
    },
    {
      "id":"J",
      "name":"SAND PIT"
    },
    {
      "id":"K",
      "name":"FIGURE OF X"
    },
    {
      "id":"L",
      "name":"LEFT REVERSE PARKING"
    },
    {
      "id":"M",
      "name":"RIGHT REVERSE PARKING"
    },
    {
      "id":"N",
      "name":"FINISHING POINT"
    },
]


  constructor(
    private fb:FormBuilder,
    private http: HttpClient,
  ){}

  ngOnInit() {
    this.fetchCourse();
    this.form = this.fb.group({
      course_id: [null,Validators.required],
      from_date: [null,Validators.required],
      to_date: [null],
    });
  }

  viewFinalReport(){
    console.log(this.form)
    this.all_reports=true;
    // this.getreports();
  }

  getreports() {
    this.http.get(this.environment.apiUrl + 'v1/report/finalReport/?course_id='+this.selected_option.id+'&from_date='+this.form.value['from_date']+'&to_date='+this.form.value['to_date']).subscribe(
      (data: any) => {
        console.log("final report",data)
        // this.individual_report = data.results;
        // if (this.individual_report.length > 0) {
        //   this.enabletable = true;
        //   console.log(this.individual_report)
        //   this.individual_report = this.individual_report.sort((a:any, b:any) => a.id - b.id);
        //   this.form.reset();
        // } else {
        //   window.alert("Trainee not exist");
        // }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );
  }

  fetchCourse() { 
    this.http.get(this.environment.apiUrl + 'v1/course/course/').subscribe(
      (data: any) => {
        console.log("Fetched course",data.results);
        this.courses = data.results
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    ); 
  }

  onSearchChange(): void {
    this.course_id = this.form.value['course_id']
    this.filteredOptions = this.courses.filter((course: any) =>
      course.name.toLowerCase().includes(this.course_id?.toLowerCase())
    );
  }
  
  selectOption(option: any): void {
    this.selected_option = option
    this.form.get('course_id')?.setValue(option.name);
    this.course_id = this.form.value['course_id'];
    this.filteredOptions = [];
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
