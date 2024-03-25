#pragma once

struct GroupManager
{
	
    void Run()
    {
		int ptnum=0;
		for(ptnum=0; ptnum<npoints(0); ptnum++)
		{
			if (ptnum > 4)
        		setpointgroup(0, "newgroup", ptnum, 1);
		}
    }
}


void Test(){

	int primnum=0;
		for(primnum=0; primnum<nprimitives(0); primnum++)
		{
			if (primnum > 0)
        		setprimgroup(0, "newgroup", primnum, 1);
		}

}