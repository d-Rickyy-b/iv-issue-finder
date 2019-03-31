function create_issue(issue_url, domain_name, author_name, creator_name, comment, reply) {
    var container = document.createElement('div');
    container.classList.add('list-item');

    container.innerHTML = `<div class="domain">
                                <a href="${issue_url}">${domain_name}</a>
                            </div>
                            <div class="issue-author name">${author_name}</div>
                            <div class="template-creator name">${creator_name}</div>
                            <div class="comment-box">
                                <div class="issue-comment comment-field">${comment}</div>
                                <div class="issue-reply comment-field">${reply}</div>
                            </div>`

    return container;
}

function filter(name) {
    list = document.getElementById("main-list");
    list.innerHTML = "";
    

    for (i = 0; i < issue_data.length; i++) {
        var issue = issue_data[i];
        console.log(issue)
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var domain_name = regExp.exec(issue.url)[1]
        if (domain_name.includes(String(name))) {
            var container = create_issue(issue.url, domain_name, issue.author, " ", issue.comment, issue.creator_comment);
            list.appendChild(container);
        }
    }
}

function remove_filter() {
    list = document.getElementById("main-list");
    list.innerHTML = "";

    issue_data.forEach(issue => {              
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var container = create_issue(issue.url, regExp.exec(issue.url)[1], issue.author, "    ", issue.comment, issue.creator_comment);
        list.appendChild(container);
    });
}

function search() {
    var text = document.getElementById("domain-search-bar").value;
    if (text === "") {
        remove_filter();
    } else {
        filter(text);
    }
}

var issue_data = [];

// ./domains.json
fetch('./issues.json')
  .then(response => {
    return response.json()
  })
  .then(data => {
    // Work with JSON data here
    issue_data = data;
    var list = document.getElementById("main-list");

    //var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;

    data.forEach(issue => {              
        var regExp = /https:\/\/instantview\.telegram\.org\/contest\/(.*?)\/template[0-9]+\/issue[0-9]+\/?/g;
        var container = create_issue(issue.url, regExp.exec(issue.url)[1], issue.author, issue.template_creator, issue.comment, issue.creator_comment);
        list.appendChild(container);
    }); 

  })
  .catch(err => {
    // Do something for an error here
    console.error(err);
  })
