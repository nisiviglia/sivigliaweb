//
//Blog page
//




//
//Projects page
//
class Label extends React.Component {
    constructor() {
        super();
        this.state = {
            style: {
                all: {
                    fontFamily: "sans-serif",
                    fontWeight: "bold",
                    padding: 13,
                    margin: 0,
                    textAlign: "center",
                },
                label: {
                    width: "30px",
                    height: "30px",
                    borderRadius: "50%",
                    fontSize: "18px",
                    color: "#000",
                    lineHeight: "30px",
                    textAlign: "center",
                    background: "#fff",
                    float: "left",
                    filter: "drop-shadow(0px 0px 1px #666)",
                    WebkitFilter: "drop-shadow(0px 0px 1px #666)",
                }
            }
        };
    }

    render(props) {
        return( 
            <div style={this.state.style.all}>
                <div style={this.state.style.label}>
                    {this.props.label} 
                </div>
            </div>
        );
    }
}

class Discription extends React.Component {
    constructor() {
        super();
        this.state = {
            style: {
                height: 150,
                backgroundColor: "#FF6663"
            }
        };
    }

    render() {
        return(
            <div style={this.state.style}>
            <h4> {this.props.title}</h4>
            <p> {this.props.dis}</p>
            </div>
        );
    }
}

class Card extends React.Component {
    constructor(){
        super();
        this.state = {
            style: {
                height: 200,
                width: 150,
                padding: 0,
                backgroundColor: "#FFF",
                filter: "drop-shadow(0px 0px 5px #666)",
                WebkitFilter: "drop-shadow(0px 0px 5px #666)",
            } 
        };
    }

    render() {
        return (
        <div style={this.state.style}>
        <Discription title={this.props.title} dis={this.props.dis}/>
        <Label label={this.props.lang}/>
        </div>
        );
    }
}

class Projects extends React.Component {
    constructor() {
        super();
        this.state = {
            data: [],
        };

        let url = "https://api.github.com/users/nisiviglia/repos";
        fetch(url).then((response) => { 
            if (response.status != 200){
                console.log("GitHub API connection failed, status code: " + response.status);
                return;
            }
		    return response.json();
        })

        .then((repos) => {
            let data = [];
            for (let i = 0; i < repos.length; i++){
                data.push([repos[i].id, repos[i].name
                        , repos[i].description, repos[i].language]);
            }
            this.setState({data});
        })

        .catch((err) => {
            console.log("Fetch Error :-S", err);
        });
    }
    
    createCard(repo){
       return <Card key={repo[0]} title={repo[1]} dis={repo[2]} lang={repo[3]}/>
    }

    render() {
        return (
        <div>
            {this.state.data.map(this.createCard)}
        </div>
        );
    }
}

//
// Sidebar
//
class Nav extends React.Component {
    constructor() {
        super();
        this.clickOpenNav = this.clickOpenNav.bind(this);
        this.clickCloseNav = this.clickCloseNav.bind(this);
        this.state = {

             styles: {
                all: {
                    fontFamily: "Lato, sams-serif",
                    marginLeft: "0px",
                    transition: "0.5s",
                }, 
                header: {
                    all: {
                        overflow: "hidden",
                        backgroundColor: "#c9c9c9",
                        paddingLeft: "7px",
                    },
                    h2: {
                        textAlign:"center",
                    },
                    openbtn: {
                        fontSize: "30px",
                        cursor: "pointer",
                        textAlign: "left",
                        padding: 5,
                        margin: 0,
                        position: "absolute",
                        display: "inline-block",
                    }
                },
                side: {
                    all: {
                        height: "100%",
                        width: 0,
                        position: "fixed",
                        zIndex: 1,
                        top: 0,
                        left: 0,
                        backgroundColor: "#111",
                        overflowX: "hidden",
                        transition: "0.5s",
                        paddingTop: "60px"
                    },
                    a: {
                        padding: "8px 8px 8px 32px",
                        testDecoration: "none",
                        fontSize: "25px",
                        color: "#818181",
                        display: "block",
                        transition: "0.3s"
                    },
                    closebtn: {
                        position: "absolute",
                        top: 9,
                        right: "25px",
                        fontSize: "36px",
                        marginLeft: "50px",
                        textDecoration: "none"
                    }
                }
            }
        };
    }
    
    clickOpenNav(event) {
            let newStyles = this.state.styles;
            newStyles.side.all.width = "250px";
            newStyles.all.marginLeft = "250px";
            this.setState({styles: newStyles});
    }
    
    clickCloseNav(event) {
    
            let newStyles = this.state.styles;
            newStyles.side.all.width = "0px";
            newStyles.all.marginLeft = "0px";
            this.setState({styles: newStyles});
    }

    render() {
        return (
            <div style={this.state.styles.all}>    
                <div style={this.state.styles.header.all}>  
                   <h2 style={this.state.styles.header.openbtn} onClick={this.clickOpenNav}>&#9776;</h2>
                   <h2 style={this.state.styles.header.h2}><b>Nicholas Siviglia</b></h2>
                </div>
                <div style={this.state.styles.side.all}>
                    <a style={this.state.styles.side.closebtn} href="javascript:void(0)" onClick={this.clickCloseNav}>&times;</a>
                    <a style={this.state.styles.side.a} href="#">Blog</a>
                    <a style={this.state.styles.side.a} href="#">Projects</a>
                    <a style={this.state.styles.side.a} href="#">About</a>
                    <a style={this.state.styles.side.a} href="#">Contact</a> 
                </div>
                <Projects/>
            </div>
        );

    }
};

ReactDOM.render(
    <Nav/>,
    document.querySelector("#container")
);  
H
