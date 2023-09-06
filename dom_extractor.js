const { Index, Document, Worker,FlexSearch } = require("flexsearch");
const { parse }=require("node-html-parser");
const {gmail_body_dom_content,gmail_home_page_dom_content,create_campaign_dom_content,contlo_dom_content,netflix_dom_content,insta_search_dom_content,
    linkedin_connect_dom_content,google_calendar_dom_content,google_dom_content,youtube_dom_content,linkedin_dom_content,jira_create_sprint,jira_create_issue,
    jira_type_issue,calendar_dom_content,calendar_event_dom_content,calendar_event_box_dom_content,hubspot_dom_content,hubspot_create_company_dom_content}=require('./dom')

// org_keyword="Click on the button ->Create company"
org_keyword="Type 'Plugin meet' in the textbox ->domain-input"
keyword=org_keyword.split('->')[1]
// keyword="create campaign"

var cnt=0
function recur(root,ans,index){
    var counter=0;
    var map={}
    if(!root | typeof(root) === 'undefined' ){
        return
    }
    // if()
    // console.log("*****",root)

    // for(var i=0;i<root.childNodes.length;i++){
    //     if(root.childNodes[i].rawAttrs){
    //         counter++
    //     }
    // }

    // console.log(counter)
    // if(root.rawAttrs && root.rawTagName!='iframe'&& root.rawTagName!='script' && root.rawTagName!='code' && root.rawTagName!='img' && root.rawTagName!='use'){
    //     // console.log("*****",root)
    //     // console.log("reached",root)
    //     ans.push(root)

    // }

    for(var i=0;i<root.childNodes.length;i++){
        // if(root.childNodes[i].rawAttrs){
        //     // console.log("child",root.childNodes[i].outerHTML)
            index.add(cnt,root.childNodes[i].outerHTML)
            map[cnt]=i
            cnt++
        // }

    }
    // console.log("crossed loop case",index.search("search"))
    const new_root_idx_arr=index.search(keyword)
    // let search_arr=keyword.split(' ')
    // // console.log("search_arr",search_arr,search_arr.length)
    // const new_root_idx_arr=[]
    // for(var temp of search_arr){
    //     if(temp.length<=2) continue
    //     // console.log("term ",temp)
    //     const temp_arr=index.search(temp)

    //     for(var temp_idx of temp_arr){
    //         new_root_idx_arr.push(temp_idx)
    //     }
    // }
    // console.log(new_root_idx_arr)

    // console.log("******root->",root.rawAttrs,new_root_idx_arr)
    // console.log("new_root_idx_arr",new_root_idx_arr)
    for(var j=0;j<new_root_idx_arr.length;j++){
        // console.log("new root",root.childNodes[new_root_idx_arr[j]])
        if(root.childNodes[map[new_root_idx_arr[j]]]  && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='iframe' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='script' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='picture' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='style' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='code' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='img' && root.childNodes[map[new_root_idx_arr[j]]].rawTagName!='use'){
            // console.log("*****",root)
            // console.log("reached",root)
            // parents[r]
            // console.log("child:",root.childNodes[map[new_root_idx_arr[j]]].tagName,root.childNodes[map[new_root_idx_arr[j]]])
            const index_to_remove = ans.indexOf(root.childNodes[map[new_root_idx_arr[j]]].parentNode);
            if (index_to_remove > -1) {
                // console.log("*****removed->",ans[index_to_remove])
                ans.splice(index_to_remove, 1);
            }

            const index_to_add=ans.indexOf(root.childNodes[map[new_root_idx_arr[j]]])
            if(index_to_add==-1){
                ans.push(root.childNodes[map[new_root_idx_arr[j]]])
                recur(root.childNodes[map[new_root_idx_arr[j]]],ans,index)
            }
        }

    }
    return
}

function dom_extractor(a){
    const root = parse(hubspot_create_company_dom_content);
    // console.log("((((root",root)
    const index = new Index({tokenize:"strict",resolution:9});


    ans=[]

    var relevant_elements=[]
    for(var i=0;i<root.childNodes.length;i++){
        if( root.childNodes[i].rawTagName!='script'){
            relevant_elements.push(root.childNodes[i])
        }
    }

    for(var i=0;i<relevant_elements.length;i++){
        // console.log("root ele",relevant_elements[i])
        recur(relevant_elements[i],ans,index)
    }

    console.log("ans",ans.length)
    res={}
    for(var i=0;i<ans.length;i++){
        ans[i]={"id":i,"rawAttrs":ans[i].rawAttrs,"rawTagName":ans[i].rawTagName,"textContent":ans[i].textContent.slice(0,20)}
        // console.log("******parent->")
//        console.log(ans[i])

//        res={...,ans[i]}
    }
    return a
}

dom_extractor()