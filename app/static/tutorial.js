const tour = new Shepherd.Tour({
    defaultStepOptions: {
        cancelIcon: {
            enabled: true
        },
        classes: 'class-1 class-2',
        scrollTo: { behavior: 'smooth', block: 'center' }
    }
});
switch (window.location.pathname) {
    case '/timer':
        //modal Timer
        tour.addStep({
            title: 'Selecione a empresa',
            text: 'Para iniciar selecione a empresa que você deseja.',
            attachTo: {
                element: '#selectCompany',
                on: 'top'
            },
            buttons: [
                {
                    action() {
                        return this.next();
                    },
                    text: 'Próximo'
                }
            ],
            id: 'selectCompany'
        });

        tour.addStep({
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

        tour.addStep({
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
        break;

    //Companies page
    case '/companies':
        tour.addStep({
            title: 'Empresas',
            text: 'Aqui é onde ficarão as empresas cadastradas, você pode clicar nelas para ser levado a tela de cada uma.',
            attachTo: {
                element: '#companiesBox',
                on: 'top'
            },
            buttons: [
                {
                    action() {
                        return this.next();
                    },
                    text: 'Próximo'
                }
            ],
            id: 'CompanyBox'
        });

        tour.addStep({
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
        break;
    //reports page
    case '/reports':
        tour.addStep({
            title: 'Empresa',
            text: 'Selecione aqui a empresa desejada para gerar o relatório.',
            attachTo: {
                element: '#selectCompany',
                on: 'top'
            },
            buttons: [
                {
                    action() {
                        return this.next();
                    },
                    text: 'Próximo'
                }
            ],
            id: 'selectCompany'
        });

        tour.addStep({
            title: 'Data de início',
            text: 'Especifique a data inicial desejada.',
            attachTo: {
                element: '#dateStart',
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
            id: 'dateStart'
        });

        tour.addStep({
            title: 'Data final',
            text: 'Especifique a data final desejada.',
            attachTo: {
                element: '#dateEnd',
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
            id: 'dateEnd'
        });

        tour.addStep({
            title: 'Gerar relatório',
            text: 'Clique aqui para gerar o relatório.',
            attachTo: {
                element: '#reportButton',
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
            id: 'reportButton'
        });
        break;
}
tour.start();

function timerTour(button){
    const tour = new Shepherd.Tour({
        defaultStepOptions: {
            cancelIcon: {
                enabled: true
            },
            classes: 'class-1 class-2',
            scrollTo: { behavior: 'smooth', block: 'center' }
        }
    });
    switch(button){
        case 'register':
            tour.addStep({
                title: 'Ficar Disponível',
                text: 'Clique aqui para ficar disponível e começar a contabilizar o tempo.',
                attachTo: {
                    element: '#'+identifier,
                    on: 'top'
                },
                buttons: [
                    {
                        action() {
                            return this.next();
                        },
                        text: 'Fechar'
                    }
                ],
                id: identifier
            });
            break;
        case 'available':
            tour.addStep({
                title: 'Começar trabalho',
                text: 'Clique aqui para começar a contabilizar o tempo de trabalho.',
                attachTo: {
                    element: '#'+identifier,
                    on: 'top'
                },
                buttons: [
                    {
                        action() {
                            return this.next();
                        },
                        text: 'Próximo'
                    }
                ],
                id: identifier
            });
            tour.addStep({
                title: 'Começar descanso',
                text: 'Clique aqui para começar a contabilizar o tempo de descanso.',
                attachTo: {
                    element: '#'+identifier,
                    on: 'top'
                },
                buttons: [
                    {
                        action() {
                            return this.next();
                        },
                        text: 'Próximo'
                    }
                ],
                id: identifier
            });
            tour.addStep({
                title: 'Encerrar trabalho',
                text: 'Clique aqui para finalizar o trabalho.',
                attachTo: {
                    element: '#'+identifier,
                    on: 'top'
                },
                buttons: [
                    {
                        action() {
                            return this.next();
                        },
                        text: 'Fechar'
                    }
                ],
                id: identifier
            });
            break;
    }
    tour.start();
}