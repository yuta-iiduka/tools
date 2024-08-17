console.log("filter.js is called.")

class Filter{
    static{
        this.cnt = 0;
        this.list = [];
        this.WORD = {OR:"OR",AND:"AND",DUMMYID:"_dummy_id"};
        this.COMPARISION = {
            EQUAL:"equal",NOT_EQUAL:"not equal",
            BIGGER:"bigger",SMALLER:"smaller",
            EQUAL_BIGGER:"equal_bigger",EQUAL_SMALLER:"equal_smaller",
            BEFORE:"before",AFTER:"after",
            EQUAL_BEFORE:"equal_before",EQUAL_AFTER:"equal_after",
            INCLUDE:"include",NOT_INCLUDE:"not include",
        };
    }

    /**
     * 条件に合わせてフィルターを行う
     * condition[or[and]];
     * condition = [
     *      [
     *          {field:"id",value:1,comparision:"==="},
     *          {field:"name",value:"your name",comparision:"in"}
     *      ],
     *      [
     *          {field:"id",value:2,comparision:">"},
     *          {field:"name",value:"him name",comparision:"==="} 
     *      ]
     * ];
     * @param {Array} condition 
     */
    constructor(condition=[],data=null){

        this.condition = condition;

        // 元データリスト
        this.data = data;
        // フィルターした結果のリストデータ
        this.result = [];

    }

    set(data){
        delete this.data;
        this.data = data;
        for(let i=0; i<this.data.length; i++){
            this.data[i][Filter.WORD.DUMMYID] = i;
        }

        return this;
    }

    set_condition(condition){
        delete this.condition;
        this.condition = condition;
        return this;
    }

    /**
     * single filter
     * @returns 
     */
    check(list=[],field="",value=null,comparision=Filter.COMPARISION.EQUAL){
        const result = list.filter(function(data){
            const d = data[field];
            if(d === undefined){ return false;}
            if( Filter.COMPARISION.EQUAL === comparision){
                return d === value;
            }else if(Filter.COMPARISION.NOT_EQUAL === comparision){
                return d !== value;
            }else if(Filter.COMPARISION.BIGGER === comparision){
                return d > value;
            }else if(Filter.COMPARISION.SMALLER === comparision){
                return d < value;
            }else if(Filter.COMPARISION.EQUAL_BIGGER === comparision){
                return d >= value;
            }else if(Filter.COMPARISION.EQUAL_SMALLER === comparision){
                return d <= value;
            }else if(Filter.COMPARISION.BEFORE === comparision){
                return new Date(d) < new Date(value);
            }else if(Filter.COMPARISION.AFTER === comparision){
                return new Date(d) > new Date(value);
            }else if(Filter.COMPARISION.EQUAL_BEFORE === comparision){
                return new Date(d) <= new Date(value);
            }else if(Filter.COMPARISION.EQUAL_AFTER === comparision){
                return new Date(d) >= new Date(value);
            }else if(Filter.COMPARISION.INCLUDE === comparision){
                return d.incldes(value);
            }else if(Filter.COMPARISION.NOT_INCLUDE === comparision){
                return !(d.incldes(value));
            }
        });
        return result;
    }

    or(or_condition){
        let result = [];
        for(let con of or_condition){
            result = result.concat(this.and(con));
        }
        return result;
    }

    and(and_condition){
        let result = this.data;
        for(let con of and_condition){
            result = this.check(result, con.field, con.value, con.comparision);
        }
        return result;
    }

    all(){
        if(this.result !== undefined && this.result !== null){
            return this.result;        
        }
        return [];
    }

    one(){
        return this.get(0);
    }

    get(index=0){
        if(this.result !== undefined && this.result !== null && this.result.length>0){
            return this.result[index] === undefined ? null : this.result[index];
        }
        return null;
    }

    map(list=[]){
        return Array.from( new Map( list.map((r) => [r[Filter.WORD.DUMMYID], r]) ).values() );
    }

    build(){
        const result = this.or(this.condition);
        this.result = this.map(result);
        return this;
    }
}


let f = new Filter();
    f.set_condition(
        [
            [{field:"id", value:4, comparision:Filter.COMPARISION.BIGGER},{field:"name", value:"e", comparision:Filter.COMPARISION.EQUAL}],
            [{field:"name", value:"a", comparision:Filter.COMPARISION.EQUAL}],
            [{field:"name", value:"a", comparision:Filter.COMPARISION.EQUAL}],
        ]
    )
    .set([
        {id:1,name:"a"},
        {id:2,name:"b"},
        {id:3,name:"c"},
        {id:4,name:"d"},
        {id:5,name:"e"},
        {id:6,name:"f"},
        {id:7,name:"g"},
        {id:1,name:"a"},
    ])
    .build();

console.log(f.all());