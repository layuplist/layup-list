LayupList.Web.CurrentTerm = function() {
    console.log("Current Term page");

    console.log("Testing JSX");
    var Hello = React.createClass({
        render: function() {
            return <div>Hello {this.props.name}</div>;
        }
    });

    ReactDOM.render(
    	<Hello name="World" />,
        document.getElementById('hello-world')
    );
};
