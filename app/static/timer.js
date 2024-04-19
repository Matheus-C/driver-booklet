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
      
      send_data(obj, path){//obj = object with the data to send, path = desired route
        fetch(path, {
          method: "POST",
          body: JSON.stringify(obj),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        });
      },

      register_mileage(){//register a mileage returning false if the mileage is not valid
        let mileage = window.prompt("enter the actual mileage of the vehicle in KM", "");
        if(mileage === null || mileage === "" || isNaN(mileage)){
            window.alert("the timer won't start/end if you don't enter a valid mileage");
            return false;
        }
        let mileage_data = {mileage: mileage,
                            idVehicle: 1,
                            eventTimestamp: Date.now(),
                            idCompany: 1,
                            idAttachment: null
                            }
        this.send_data(mileage_data, '/vehicle/mileage');
        return true;
      },

      timeEventHandler(type,eventType) {
        let time_now = new Date().getTime();
        let event_obj = {};
        event_obj = {
          idType: null,
          eventTimestamp: time_now,
          idUser: null,
          idVehicle: 1
        };
        this.send_data(event_obj, '/event_data');
        
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
                if(this.hours + this.minutes + this.seconds === 0){
                  if(!this.register_mileage()){
                    break;
                  }
                  this.startTimer();
                }
                this.isAvailable = true;
                time_now = Date.now();
                this.availableTimeStart = time_now;
                event_obj.idType = 5;
              }
              else if(this.isAvailable && eventType === 'end'){// id: 6
                this.isAvailable = false;
                time_now = Date.now();
                this.availableTime += time_now - this.availableTimeStart;
                event_obj.idType = 6;
              }
              break;

            default:
                console.log("Unknown type");
        }
        if(event_obj.idType !== null){
          this.send_data(event_obj, "/event_data");
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
        this.timeEventHandler("rest","start");
        this.timeEventHandler("work","end");
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

      becomeAvailable(){
        if (!this.isAvailable){
          if(this.isResting){
            this.timeEventHandler("rest","end");

          }
          this.timeEventHandler("available","start")
        }
      },

      endTimer(){
        let confirm_action = confirm('Quer mesmo acabar o dia ?');
        if (confirm_action){
          if(!this.register_mileage()){
            return;
          }
          this.timeEventHandler("work","end");
          this.timeEventHandler("available","end");
          this.timeEventHandler("rest","end");
          this.workedTime = 0;
          this.timerRunning =  false;
          this.resetTimer();
        }
        

      },
      
      enableLocation() {
        navigator.geolocation.watchPosition((position) => {
          
          const newCoords = { lat: position.coords.latitude, lon: position.coords.longitude };
          
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
