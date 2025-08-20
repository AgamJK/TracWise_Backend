import { SignUp } from '@clerk/clerk-react'

const SignUpPage = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-600 mt-2">Sign up to get started</p>
        </div>
        <SignUp 
          routing="path" 
          path="/sign-up" 
          redirectUrl="/chat"
          signInUrl="/sign-in"
        />
      </div>
    </div>
  )
}

export default SignUpPage
