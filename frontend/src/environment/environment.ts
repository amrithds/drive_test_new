
// export const environment = {
//     production: false,
//     apiUrl:'http://localhost:8000/'
//     // apiUrl: 'http://192.168.1.109:8000/',
//   }; 

  export const environment = {
    production: false,
    get apiUrl() {
      const ipAddress = window.location.hostname;
      return `http://${ipAddress}:8000/`;
    }
  };
