
switch(window.location.pathname){
    case '/timer':
        const tourModalTimer = new Shepherd.Tour({
            id: 'modalTimer',
            defaultStepOptions: {
            cancelIcon: {
                enabled: true
            },
            classes: 'class-1 class-2',
            scrollTo: { behavior: 'smooth', block: 'center' }
            }
        });

        tourModalTimer.addStep({
            title: 'Selecione a empresa',
            text: 'Para iniciar selecione a empresa que você deseja.',
            attachTo: {
            element: '#selectCompany',
            on: 'top'
            },
            buttons: [
            {
                action() {
                return this.back();
                },
                classes: 'shepherd-button-secondary',
                text: 'Voltar'
            },
            {
                action() {
                return this.next();
                },
                text: 'Próximo'
            }
            ],
            id: 'selectCompany'
        });

        tourModalTimer.addStep({
            title: 'Selecionar veículo',
            text: 'Agora selecione o carro que você deseja.',
            attachTo: {
            element: '#selectVehicle',
            on: 'top'
            },
            buttons: [
            {
                action() {
                return this.back();
                },
                classes: 'shepherd-button-secondary',
                text: 'Voltar'
            },
            {
                action() {
                return this.next();
                },
                text: 'Próximo'
            }
            ],
            id: 'selectCar'
        });

        tourModalTimer.addStep({
            title: 'Quilometragem',
            text: 'Agora selecione a quilometragem atual do veículo.',
            attachTo: {
            element: '#mileage',
            on: 'top'
            },
            buttons: [
            {
                action() {
                return this.back();
                },
                classes: 'shepherd-button-secondary',
                text: 'Voltar'
            },
            {
                action() {
                return this.next();
                },
                text: 'Fechar'
            }
            ],
            id: 'mileage'
        });
        tourModalTimer.start();
        break;
    
    //Companies page
    case '/companies':
        const tourCompanies = new Shepherd.Tour({
            id: 'companies',
            defaultStepOptions: {
            cancelIcon: {
                enabled: true
            },
            classes: 'class-1 class-2',
            scrollTo: { behavior: 'smooth', block: 'center' }
            }
        });

        tourCompanies.addStep({
            title: 'Empresas',
            text: 'Aqui é onde ficarão as empresas cadastradas, você pode clicar nelas para ser levado a tela de cada uma.',
            attachTo: {
            element: '#companiesBox',
            on: 'top'
            },
            buttons: [
            {
                action() {
                return this.back();
                },
                classes: 'shepherd-button-secondary',
                text: 'Voltar'
            },
            {
                action() {
                return this.next();
                },
                text: 'Próximo'
            }
            ],
            id: 'CompanyBox'
        });

        tourCompanies.addStep({
            title: 'Cadastrar nova empresa',
            text: 'Você pode adicionar uma nova empresa clicando aqui.',
            attachTo: {
            element: '#add_new_company_button',
            on: 'top'
            },
            buttons: [
            {
                action() {
                return this.back();
                },
                classes: 'shepherd-button-secondary',
                text: 'Voltar'
            },
            {
                action() {
                return this.next();
                },
                text: 'Fechar'
            }
            ],
            id: 'addNewCompany'
        });

        tourCompanies.start();
        break;
    
        
  }
  
  