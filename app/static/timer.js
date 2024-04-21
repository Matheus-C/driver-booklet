//window.app = 
function stopwatch() {
    return {
      workingTimeStart: 0,
      workedTime: 0,
      availableTimeStart: 0,
      availableTime: 0,
      restTimeStart: 0,
      restTime: 0,
      isAvailable: false,
      isResting: false,
      isWorking: false,
      timer: null,
      timerRunning: false,
      locationEnabled: false,
      hours: 0,
      minutes: 0,
      seconds: 0,
      initialCoords: {lat: 0, lon: 0}, // Initial coordinates
      isModalVisible:true,
      currentMileage:null,
      idCompany:null,
      idVehicle:null,
      currentCoords: {lat: 0, lon: 0},
      
      send_data(obj,method,path){
        if (method ===  "GET"){
          return fetch(path, {
            method: method,
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          }).then(response => response.json());
        }
      else if (method === "POST"){
        return fetch(path, {
          method: method,
          body: JSON.stringify(obj),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        }).then(response => response.json());
      }
       
      },

      sendAttachment(){//it must return the id of the attachment
        return null;
      },

      sendMileage(){
        let mileage_num = document.getElementById('mileage').value;
        let mileage_data = {mileage: mileage_num,
                            idVehicle: this.idVehicle,
                            eventTimestamp: Date.now(),
                            idCompany: this.idCompany,
                            idAttachment: this.sendAttachment(),
                            idType: null
                            }
        if(this.hours+this.minutes+this.seconds === 0){
          mileage_data.idType = 7;
        }else{
          mileage_data.idType = 8;
        }
        this.send_data(mileage_data,"POST",'/vehicle/mileage');
        this.isModalVisible=false;
        this.resetTimer();
        this.update_latest_from_db()
      },

      timeEventHandler(type,eventType) {
        let time_now = new Date().getTime();
        let event_obj = {};
        event_obj = {
          idType: null,
          idCompany: this.idCompany,
          eventTimestamp: time_now,
          idVehicle: this.idVehicle,
          geolocation: this.currentCoords.lat + ',' + this.currentCoords.lon
        };
                
        switch (type) {
            case "work":// id: 1
                if (!this.isWorking && eventType === 'start' ) {
                  this.timeEventHandler("available","end");
                  this.isWorking = true;
                  this.workingTimeStart = time_now;
                  event_obj.idType = 1;
                }
                else if (this.isWorking && eventType === 'end') {// id: 2
                  this.isWorking = false;
                  this.workedTime += time_now - this.workingTimeStart;
                  event_obj.idType = 2;
                }
              
            break;
            
            case "rest":// id: 3
              if (!this.isResting && eventType === 'start') {
                  this.isResting = true;
                  this.restTimeStart = time_now;
                  event_obj.idType = 3;
              }
              else if (this.isResting && eventType === 'end'){// id: 3
                this.isResting = false;
                this.restTime += time_now - this.restTimeStart;
                event_obj.idType = 4;
              }
              break;
            
            case "available":// id: 5
              if (!this.isAvailable && eventType === 'start') {
                this.startTimer();
                this.isAvailable = true;
                time_now = Date.now(); //#todo
                this.availableTimeStart = time_now;
                event_obj.idType = 5;
              }
              else if(this.isAvailable && eventType === 'end'){// id: 6
                this.isAvailable = false;
                time_now = Date.now();//#todo
                this.availableTime += time_now - this.availableTimeStart;
                event_obj.idType = 6;
              }
              break;

            default:
                console.log("Unknown type");
        }
        if(event_obj.idType !== null){
          this.send_data(event_obj,"POST","/event_data");
        }
    },

      startTimer() {
        if (!this.timerRunning)
        {
          this.timerRunning = true;
          this.timer = setInterval(() => {
          this.seconds++;
          if (this.seconds === 10) {
            if(this.isWorking){
              const postData = {
                title: "Generic Title",
                body: "Generic Body"
              };
              fetch('/admin-api/trigger-push-notifications', {
                method: "POST",
                body: JSON.stringify(postData),
                headers: {
                  "Content-type": "application/json; charset=UTF-8"
                }
              });
            }
          }
          if (this.seconds === 60) {
            this.seconds = 0;
            this.minutes++;
          }
          if (this.minutes === 60) {
            this.minutes = 0;
            this.hours++;
            if(this.isWorking && (this.workedTime + (Date.now()-this.workingTimeStart)) >= 3600000*7){
              new Notification('Notificação Teste > 7Hrs', {
              body: 'body',
              icon: "{{ url_for('static', filename='notification.ico') }}",
              tag: 'tag',
              data: 'data'
              });
            }
          }
        }, 1000);
        }
        else{
          this.timeEventHandler("work",'start');
        }
        
      },
      
      stopTimer() {
        clearInterval(this.timer);
        this.timerRunning = false;
        this.timeEventHandler("work","end");
        this.timeEventHandler("rest","start");
        this.timeEventHandler("available","end");

      },
      
      resetTimer() {
        clearInterval(this.timer);
        this.hours = 0;
        this.minutes = 0;
        this.seconds = 0;
        this.timerRunning = false;
      },
      
      get formattedTime() {
        let currentTime = String(this.hours).padStart(2, '0') + ':' +
        String(this.minutes).padStart(2, '0') + ':' +
        String(this.seconds).padStart(2, '0');
        return (
          currentTime
        );
      },

      update_latest_from_db()
      {
        if(this.hours+this.minutes+this.seconds === 0){
          response = this.send_data(null,'GET','/vehicle/last_state/'+this.idVehicle)
          .then(data =>{
            if (data.eventTime != null){
                const givenTime = new Date(Date.parse(data.eventTime));
                const currentTime = new Date();
                const timeDifference =  currentTime - givenTime;
  
                const hoursDifference = Math.floor(timeDifference / (1000 * 60 * 60));
                const minutesDifference = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
                const secondsDifference = Math.floor((timeDifference % (1000 * 60)) / 1000);
                console.log(data.eventName)
                if (data.eventName.includes('_start')){
                  this.hours = hoursDifference;
                  this.minutes = minutesDifference;
                  this.seconds = secondsDifference;
                  if (data.eventName.includes('availability')){
                      this.isAvailable = true;
                  }
                  if (data.eventName.includes('rest')){
                      this.isResting = true;
                  }
                  if (data.eventName.includes('work')){
                      this.isWorking = true;
                  }
                  this.startTimer() 
                  console.log(`Time Difference: ${hoursDifference} hours,
                  ${minutesDifference} minutes, ${secondsDifference} seconds`)
              }
      
            }
          })
          
        }
      },

      becomeAvailable(){
       if (!this.isAvailable) {
            if(this.isResting){
              this.timeEventHandler("rest","end");
            }
            this.timeEventHandler("available","start")
          }
      },

      endTimer(){
        if (confirm('Quer mesmo acabar o dia ?')){
          this.timeEventHandler("work","end");
          this.timeEventHandler("available","end");
          this.timeEventHandler("rest","end");
          this.workedTime = 0;
          this.timerRunning =  false;
          this.isModalVisible = true;
        }
      },
      
      enableLocation() {
        navigator.geolocation.watchPosition((position) => {
          
          const newCoords = { lat: position.coords.latitude, lon: position.coords.longitude };
          this.currentCoords = newCoords;
          if (this.isAvailable && this.distance_ari(this.initialCoords, newCoords) >= 0.00003) { // Only start timer after initial location
            this.startTimer();
          } else {
            this.initialCoords = newCoords;
          }

        });
        this.locationEnabled = true;
      },

    distance_ari(coord1, coord2) {
      
      let pow_lat = Math.pow((coord1.lat - coord2.lat),2)
      let pow_lon = Math.pow((coord1.lon - coord2.lon),2)
      let d = Math.sqrt(pow_lat+pow_lon)
      
      return d
    },

  }

}
