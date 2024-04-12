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

      timeEventHandler(type,eventType) {
        let time_now = new Date().getTime();
        let event_obj = {};
        event_obj = {
          idType: null,
          eventTimestamp: time_now,
          idUser: 1,
          vehicleId: 1
        };
        function send_json(obj){
          fetch('/event_data', {
          method: "POST",
          body: JSON.stringify(obj),
          headers: {
            "Content-type": "application/json; charset=UTF-8"
          }
        }).then((response) => response.json()).then((json) => console.log(json));
        }
        
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
                  console.log(this.workedTime);
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
          send_json(event_obj);
        }
    },

      /*start(type){
        if(type==="work"){
          this.workingTimeStart = this.initiate(this.isWorking,true)
          if(!this.isWorking){
            this.end("available");
            this.isWorking = true;
            this.workingTimeStart = Date.now();
          }
        }else if(type === "rest"){
          if(!this.isResting){
            this.isResting = true;
            this.restTimeStart = Date.now();
          }
        }else if(type === "available"){
          this.availableTimeStart = this.initiate(this.isAvailable,true)
          if(!this.isAvailable){
            this.isAvailable = true;
            this.availableTimeStart = Date.now();
          }
        }
      },*/

      /*end(type){
        if(type==="work"){
          if(this.isWorking){
            this.isWorking = false;
            this.workedTime += Date.now() - this.workingTimeStart;
          }
        }else if(type === "rest"){
          if(this.isResting){
            this.isResting = false;
            this.restTime += Date.now() - this.restTimeStart;
          }
        }else if(type === "available"){
          if(this.isAvailable){
            this.isAvailable = false;
            this.availableTime += Date.now() - this.availableTimeStart;
          }
        }
      },*/

      startTimer() {
        if (!this.timerRunning)
        {
          this.timerRunning = true;
          this.timer = setInterval(() => {
          this.seconds++;
          if (this.seconds === 10) {
            if(this.isWorking && (this.workedTime + Date.now()-this.workingTimeStart) >= 5000){
              let notification = new Notification('Notificação Teste 10s', {
              body: 'body',
              icon: "{{ url_for('static', filename='notification.ico') }}",
              tag: 'tag',
              data: 'data'
              });
              setTimeout(notification.close.bind(notification), 4000);
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
          console.log('Inicio da condução');
          this.timeEventHandler("work",'start');
          //this.start("work");

        }
        
      },
      
      stopTimer() {
        console.log('Fim da condução');
        clearInterval(this.timer);
        this.timerRunning = false;
        //this.end("work");
        //this.end("available");
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
        return (
          String(this.hours).padStart(2, '0') + ':' +
          String(this.minutes).padStart(2, '0') + ':' +
          String(this.seconds).padStart(2, '0')
        );
      },

      becomeAvailable(){
        if (!this.isAvailable){
          if(this.isResting){
            //this.end("rest");
            this.timeEventHandler("rest","end");

          }
          this.timeEventHandler("available","start")
          //this.start("available");
          console.log('Inicio do dia ou atividade');
          this.startTimer();
        }
      },

      endTimer(){
        let confirm_action = confirm('Quer mesmo acabar o dia ?');
        if (confirm_action){
          //this.initialLocationReceived = false;
          this.timeEventHandler("work","end");
          this.timeEventHandler("available","end");
          this.timeEventHandler("rest","end");
          //this.end("work");
          //this.end("available");
          //this.end("rest");
          this.workedTime = 0;
          this.timerRunning =  false;
          console.log ('fim de expediente ->'+ this.formattedTime);
          this.resetTimer();
        }
        

      },
      
      enableLocation() {
        navigator.geolocation.watchPosition((position) => {
          
          const newCoords = { lat: position.coords.latitude, lon: position.coords.longitude };
          
          console.log('dist ari: '+ this.distance_ari(this.initialCoords, newCoords))
          
          if (this.isAvailable && this.distance_ari(this.initialCoords, newCoords) >= 0.00003) { // Only start timer after initial location
            console.log('dist ari ativ: '+ this.distance_ari(this.initialCoords, newCoords))
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
