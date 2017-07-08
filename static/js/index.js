
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
            </div>
        );

    }
};

ReactDOM.render(
    <Nav/>,
    document.querySelector("#container")
);  


